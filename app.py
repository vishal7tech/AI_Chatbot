# app.py (full corrected version)

from flask import Flask, jsonify, request, render_template_string
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
from flask import render_template 

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# ── Admin Routes ────────────────────────────────────────────────
@app.route('/admin/rules', methods=['GET'])
def get_rules():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rules ORDER BY id")
        rules = cursor.fetchall()
        return jsonify(rules)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/rules', methods=['POST'])
def add_rule():
    data = request.json
    pattern = data.get('pattern')
    response = data.get('response')
    if not pattern or not response:
        return jsonify({"error": "Pattern and response required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rules (pattern, response) VALUES (%s, %s)", (pattern, response))
        conn.commit()
        return jsonify({"message": "Rule added", "id": cursor.lastrowid}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/rules/<int:rule_id>', methods=['PUT'])
def edit_rule(rule_id):
    data = request.json
    pattern = data.get('pattern')
    response = data.get('response')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE rules SET pattern=%s, response=%s WHERE id=%s", (pattern, response, rule_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Rule not found"}), 404
        return jsonify({"message": "Rule updated"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rules WHERE id=%s", (rule_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Rule not found"}), 404
        return jsonify({"message": "Rule deleted"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ── Chat Endpoint ───────────────────────────────────────────────
@app.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({"error": "Please send JSON data"}), 400

    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"response": "Bhai kuch to type karo yaar! 😅"}), 400

    user_lower = user_message.lower()
    response = "Sorry, samajh nahi aaya... Try: hi, fees, appointment, bye"
    matched_rule = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get normal rules
        cursor.execute("SELECT pattern, response FROM rules WHERE pattern != 'default'")
        rules = cursor.fetchall()

        # 1. Exact match
        for rule in rules:
            if rule['pattern'].lower() == user_lower:
                matched_rule = rule
                break

        # 2. Contains match
        if not matched_rule:
            for rule in rules:
                if rule['pattern'].lower() in user_lower:
                    matched_rule = rule
                    break

        # 3. Default fallback
        if not matched_rule:
            cursor.execute("SELECT response FROM rules WHERE pattern = 'default'")
            default = cursor.fetchone()
            if default:
                response = default['response']

        if matched_rule:
            response = matched_rule['response']

        # Log the chat
        cursor.execute(
            "INSERT INTO chat_logs (user_message, bot_response) VALUES (%s, %s)",
            (user_message, response)
        )
        conn.commit()

        return jsonify({"response": response})

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ── Home (for browser test) ─────────────────────────────────────
  # ← Yeh line already hai toh nahi daalna

@app.route('/')
def chat_ui():
    return render_template('chat.html')
@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)