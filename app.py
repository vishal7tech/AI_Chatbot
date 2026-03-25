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
import random
from nltk.corpus import stopwords
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import threading

# Global model variables
model = None
vectorizer = None
label_encoder = None

def load_local_models():
    global model, vectorizer, label_encoder
    try:
        model = load_model('intent_model.h5')
        vectorizer = joblib.load('vectorizer.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
        print("NLP Models loaded successfully from disk!")
    except Exception as e:
        print(f"Warning: NLP models not found or failed to load: {e}")

load_local_models()

# ────────────────────────────────────────────────
#          1. Helper Functions – FIRST
# ────────────────────────────────────────────────

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'Vishal@74'),
        database=os.getenv('DB_NAME', 'chatbot_db')
    )

# ────────────────────────────────────────────────
#          2. NLP Globals + Functions
# ────────────────────────────────────────────────

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    # Enhanced stopwords with Indian English
    custom_stopwords = {'hai', 'hain', 'ho', 'ki', 'ko', 'ke', 'ka', 'bhi', 'mein', 'par', 'aur', 'lekin', 'kyunki'}
    all_stopwords = stop_words.union(custom_stopwords)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum() and word not in all_stopwords]
    return ' '.join(tokens)

def reload_nlp_model():
    # Only reload the files from disk, don't refit
    load_local_models()

def train_model_thread():
    try:
        print("Starting AI model training...")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Load intents & patterns
        cursor.execute("SELECT id, tag FROM intents")
        intents_data = cursor.fetchall()
        
        patterns = []
        labels = []
        for intent in intents_data:
            cursor.execute("SELECT pattern FROM patterns WHERE intent_id = %s", (intent['id'],))
            intent_patterns = cursor.fetchall()
            for p in intent_patterns:
                patterns.append(p['pattern'])
                labels.append(intent['tag'])
                
        cursor.close()
        conn.close()
        
        if not patterns:
            print("No patterns found for training.")
            return
            
        cleaned_patterns = [clean_text(p) for p in patterns]
        
        # Enhanced vectorizer with better parameters
        new_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True
        )
        X = new_vectorizer.fit_transform(cleaned_patterns).toarray()
        
        new_label_encoder = LabelEncoder()
        y = new_label_encoder.fit_transform(labels)
        y_cat = to_categorical(y)
        
        if len(y_cat[0]) == 0 or len(X[0]) == 0:
            print("Insufficient data for training.")
            return
            
        # Enhanced model architecture
        # Split for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y_cat, test_size=0.2, random_state=42, stratify=y
        )
        
        # Build enhanced model
        new_model = Sequential([
            Input(shape=(X_train.shape[1],)),
            Dense(128, activation='relu'),
            Dropout(0.5),
            Dense(64, activation='relu'),
            Dropout(0.4),
            Dense(32, activation='relu'),
            Dropout(0.3),
            Dense(y_train.shape[1], activation='softmax')
        ])
        
        new_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        
        # Early stopping
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=0
        )
        
        # Train with validation
        new_model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=100,
            batch_size=8,
            callbacks=[early_stopping],
            verbose=0
        )
        
        # Save
        new_model.save('intent_model.h5')
        joblib.dump(new_vectorizer, 'vectorizer.pkl')
        joblib.dump(new_label_encoder, 'label_encoder.pkl')
        
        # Reload in memory
        reload_nlp_model()
        print("Model training completed successfully!")
        
    except Exception as e:
        print(f"Training failed: {e}")

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
        return jsonify({"response": "Kuch type karo!"})

    # Preprocess same as training
    clean = clean_text(user_message)  # Use same clean_text function (copy from notebook)
    if not clean.strip():
        return jsonify({"response": "Sorry, samajh nahi aaya."})

    try:
        if vectorizer is None or model is None or label_encoder is None:
            return jsonify({"response": "Model is not trained yet. Go to Admin Panel and click 'Train AI Model'."})

        vec = vectorizer.transform([clean]).toarray()
        pred = model.predict(vec, verbose=0)
        intent_idx = np.argmax(pred)
        confidence = float(np.max(pred))  # To show

        if confidence > 0.6:  # Higher threshold for DL
            predicted_tag = label_encoder.inverse_transform([intent_idx])[0]
            
            # Get random response from responses table
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT response_text FROM responses WHERE intent_id = (SELECT id FROM intents WHERE tag = %s) ORDER BY RAND() LIMIT 1", (predicted_tag,))
            resp = cursor.fetchone()
            response = resp['response_text'] if resp else "Got it!"
            cursor.close()
            conn.close()
        else:
            # Fallback
            fallback_resp = "Sorry bhai, thoda clear bolo. Try: hi, fees, bye"
            response = fallback_resp
    except Exception as e:
        print(f"Prediction error: {e}")
        response = "Oops! Something went wrong with the AI prediction."
        confidence = 0.0

    # Log
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_logs (user_message, bot_response) VALUES (%s, %s)", (user_message, response))
        conn.commit()
    except:
        pass
    finally:
        cursor.close()
        conn.close()

    return jsonify({"response": response, "confidence": round(confidence * 100, 2)})

@app.route('/api/train', methods=['POST'])
def trigger_training():
    thread = threading.Thread(target=train_model_thread)
    thread.start()
    return jsonify({"message": "AI Model Training Started in Background! Please wait a moment."})

# Your / and /admin routes go here

@app.route('/')
def chat_ui():
    return render_template('chat.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/chatlog')
def chatlog_page():
    return render_template('chatlog.html')

@app.route('/api/chatlogs', methods=['GET'])
def get_chat_logs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get chat logs ordered by timestamp (newest first)
        cursor.execute("""
            SELECT id, user_message, bot_response, timestamp 
            FROM chat_logs 
            ORDER BY timestamp DESC
        """)
        
        chat_logs = cursor.fetchall()
        
        # Format timestamp if needed
        for log in chat_logs:
            if log['timestamp']:
                # Ensure timestamp is in string format
                log['timestamp'] = str(log['timestamp'])
        
        return jsonify(chat_logs)
        
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ────────────────────────────────────────────────
#          Admin Panel Routes – Intents & Patterns
# ────────────────────────────────────────────────

@app.route('/admin/intents', methods=['GET'])
def get_intents():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT i.id, i.tag, (SELECT response_text FROM responses WHERE intent_id = i.id LIMIT 1) as response FROM intents i ORDER BY i.id")
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
            "INSERT INTO intents (tag) VALUES (%s)",
            (tag,)
        )
        new_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO responses (intent_id, response_text) VALUES (%s, %s)",
            (new_id, response)
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
            "UPDATE intents SET tag = %s WHERE id = %s",
            (tag, intent_id)
        )
        
        # For simplicity, update the first existing response or insert if not exists
        cursor.execute("SELECT id FROM responses WHERE intent_id = %s LIMIT 1", (intent_id,))
        resp_row = cursor.fetchone()
        if resp_row:
            cursor.execute("UPDATE responses SET response_text = %s WHERE id = %s", (response, resp_row[0]))
        else:
            cursor.execute("INSERT INTO responses (intent_id, response_text) VALUES (%s, %s)", (intent_id, response))
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
@app.route('/admin/patterns', methods=['GET'])
def get_patterns():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT p.id, p.intent_id, p.pattern, i.tag FROM patterns p LEFT JOIN intents i ON p.intent_id = i.id ORDER BY p.id")
        patterns = cursor.fetchall()
        return jsonify(patterns)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

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


@app.route('/admin/patterns/<int:pattern_id>', methods=['PUT'])
def update_pattern(pattern_id):
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    pattern = data.get('pattern')

    if not pattern:
        return jsonify({"error": "Pattern text required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE patterns SET pattern = %s WHERE id = %s",
            (pattern, pattern_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Pattern not found"}), 404
        reload_nlp_model()          # Important – model refresh
        return jsonify({"message": "Pattern updated"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ────────────────────────────────────────────────
#          Admin Panel Routes – Responses
# ────────────────────────────────────────────────

@app.route('/admin/responses/<int:intent_id>', methods=['GET'])
def get_responses(intent_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, response_text FROM responses WHERE intent_id = %s ORDER BY id", (intent_id,))
        responses = cursor.fetchall()
        return jsonify(responses)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/responses', methods=['POST'])
def add_response():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400
    
    data = request.get_json()
    intent_id = data.get('intent_id')
    response_text = data.get('response_text')
    
    if not intent_id or not response_text:
        return jsonify({"error": "intent_id and response_text required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO responses (intent_id, response_text) VALUES (%s, %s)",
            (intent_id, response_text)
        )
        conn.commit()
        reload_nlp_model()
        return jsonify({"message": "Response added"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/responses/<int:response_id>', methods=['DELETE'])
def delete_response(response_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM responses WHERE id = %s", (response_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Response not found"}), 404
        reload_nlp_model()
        return jsonify({"message": "Response deleted"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)