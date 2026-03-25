import mysql.connector

def run_migration():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vishal@74",
        database="chatbot_db"
    )
    cursor = conn.cursor()

    queries = [
        """CREATE TABLE IF NOT EXISTS responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            intent_id INT NOT NULL,
            response_text TEXT NOT NULL,
            FOREIGN KEY (intent_id) REFERENCES intents(id) ON DELETE CASCADE
        )""",
        "INSERT INTO responses (intent_id, response_text) SELECT id, response FROM intents",
        "ALTER TABLE intents DROP COLUMN response"
    ]

    for q in queries:
        try:
            cursor.execute(q)
            conn.commit()
            print("Success:", q.strip()[:50])
        except Exception as e:
            print("Error:", e, "on query:", q.strip()[:50])
            
    # Try inserting some sample data for intent_id=1
    try:
        cursor.execute("""
            INSERT INTO responses (intent_id, response_text) VALUES 
            (1, 'Hello! Kaise ho? 😊'),
            (1, 'Hi there! Kya chal raha hai?'),
            (1, 'Namaste! Help chahiye?')
        """)
        conn.commit()
        print("Inserted sample data for intent 1")
    except Exception as e:
        print("Error inserting sample data:", e)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    run_migration()
