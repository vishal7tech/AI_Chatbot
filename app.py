from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ────────────────────────────────────────────────
#          1. Helper Functions – FIRST
# ────────────────────────────────────────────────

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# ────────────────────────────────────────────────
#          2. NLP Globals + Functions
# ────────────────────────────────────────────────

lemmatizer = WordNetLemmatizer()
intents = []
flat_patterns = []
vectorizer = None
X = None

def clean_text(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum()]
    return ' '.join(tokens)

def reload_nlp_model():
    global intents, flat_patterns, vectorizer, X
    
    try:
        conn = get_db_connection()           # now safe – function already defined
        cursor = conn.cursor(dictionary=True)
        
        # Load intents
        cursor.execute("SELECT * FROM intents")
        intents_data = cursor.fetchall()
        intents_dict = {row['id']: {'tag': row['tag'], 'response': row['response'], 'patterns': []} for row in intents_data}
        
        # Load patterns
        cursor.execute("SELECT * FROM patterns")
        for row in cursor.fetchall():
            if row['intent_id'] in intents_dict:
                intents_dict[row['intent_id']]['patterns'].append(row['pattern'])
        
        intents = list(intents_dict.values())
        
        # Build flat list for TF-IDF
        flat_patterns = []
        for intent in intents:
            for pattern in intent['patterns']:
                flat_patterns.append({'intent': intent, 'pattern': pattern})
        
        if not flat_patterns:
            print("Warning: No patterns found!")
            cursor.close()
            conn.close()
            return
        
        # Preprocess corpus
        corpus = [clean_text(fp['pattern']) for fp in flat_patterns]
        
        vectorizer = TfidfVectorizer()
        vectorizer.fit(corpus)
        X = vectorizer.transform(corpus)
        
        cursor.close()
        conn.close()
        print("NLP Model reloaded successfully!")
        
    except Error as e:
        print(f"Database error during reload: {e}")
    except Exception as e:
        print(f"Unexpected error in reload_nlp_model: {e}")

# ────────────────────────────────────────────────
#          3. NLTK Download + env + Flask app
# ────────────────────────────────────────────────

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Load NLP model AFTER everything is defined
reload_nlp_model()

# ────────────────────────────────────────────────
#          4. All Routes (admin, chat, ui, etc.)
# ────────────────────────────────────────────────

# Your existing admin routes (/admin/rules GET/POST/PUT/DELETE) go here
# Your /chat route goes here
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({"response": "Kuch type karo na!"})

    # Preprocess user input
    user_clean = clean_text(user_message)
    if not user_clean.strip():
        return jsonify({"response": "Sorry, samajh nahi aaya."})

    user_vec = vectorizer.transform([user_clean])
    sims = cosine_similarity(user_vec, X)[0]
    max_sim = np.max(sims)

    if max_sim > 0.4:  # Adjust threshold if needed
        idx = np.argmax(sims)
        matched_intent = flat_patterns[idx]['intent']
        response = matched_intent['response']
    else:
        # Fallback
        fallback = next((i for i in intents if i['tag'] == 'fallback'), None)
        response = fallback['response'] if fallback else "Sorry, samajh nahi aaya. Try: hi, fees, bye"

    # Log to DB
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (user_message, bot_response) VALUES (%s, %s)",
            (user_message, response)
        )
        conn.commit()
    except Error as e:
        print("Log error:", e)
    finally:
        cursor.close()
        conn.close()

    return jsonify({"response": response})
# Your / and /admin routes go here

@app.route('/')
def chat_ui():
    return render_template('chat.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

# ────────────────────────────────────────────────
#          Admin Panel Routes – Intents & Patterns
# ────────────────────────────────────────────────

@app.route('/admin/intents', methods=['GET'])
def get_intents():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM intents ORDER BY id")
        intents_list = cursor.fetchall()
        return jsonify(intents_list)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/intents', methods=['POST'])
def add_intent():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400
    
    data = request.get_json()
    tag = data.get('tag')
    response = data.get('response')
    
    if not tag or not response:
        return jsonify({"error": "Tag and response required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO intents (tag, response) VALUES (%s, %s)",
            (tag, response)
        )
        conn.commit()
        new_id = cursor.lastrowid
        reload_nlp_model()  # Important: model refresh
        return jsonify({"message": "Intent added", "id": new_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/intents/<int:intent_id>', methods=['PUT'])
def update_intent(intent_id):
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400
    
    data = request.get_json()
    tag = data.get('tag')
    response = data.get('response')
    
    if not tag or not response:
        return jsonify({"error": "Tag and response required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE intents SET tag = %s, response = %s WHERE id = %s",
            (tag, response, intent_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Intent not found"}), 404
        reload_nlp_model()
        return jsonify({"message": "Intent updated"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/intents/<int:intent_id>', methods=['DELETE'])
def delete_intent(intent_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM intents WHERE id = %s", (intent_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Intent not found"}), 404
        reload_nlp_model()
        return jsonify({"message": "Intent deleted (patterns bhi delete hue)"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Patterns Routes
@app.route('/admin/patterns', methods=['POST'])
def add_pattern():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400
    
    data = request.get_json()
    intent_id = data.get('intent_id')
    pattern = data.get('pattern')
    
    if not intent_id or not pattern:
        return jsonify({"error": "intent_id and pattern required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patterns (intent_id, pattern) VALUES (%s, %s)",
            (intent_id, pattern)
        )
        conn.commit()
        reload_nlp_model()
        return jsonify({"message": "Pattern added"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/patterns/<int:pattern_id>', methods=['DELETE'])
def delete_pattern(pattern_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patterns WHERE id = %s", (pattern_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Pattern not found"}), 404
        reload_nlp_model()
        return jsonify({"message": "Pattern deleted"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)