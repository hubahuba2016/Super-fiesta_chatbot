import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# === DATABASE SETUP ===
DB_NAME = 'chatbot.db'

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatbot (
            question TEXT PRIMARY KEY,
            answer TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn, cursor

# === IMPORT TRAINING DATA FROM FILE ===
def import_training_data(cursor, conn, filename='chatbot_training_data.txt'):
    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    question, answer = None, None
    for line in lines:
        line = line.strip()
        if line.startswith("Q: "):
            question = line[3:].strip().lower()
        elif line.startswith("A: "):
            answer = line[3:].strip()
            if question and answer:
                cursor.execute("INSERT OR REPLACE INTO chatbot (question, answer) VALUES (?, ?)", (question, answer))
                question, answer = None, None

    conn.commit()
    print("Training data imported successfully.")

# === TRAINING ===
def train_bot(cursor, conn):
    print("Training mode. Add a new question-answer pair.")
    question = input("Question: ").strip().lower()
    answer = input("Answer: ").strip()

    if question and answer:
        cursor.execute("INSERT OR REPLACE INTO chatbot (question, answer) VALUES (?, ?)", (question, answer))
        conn.commit()
        print("Training saved.\n")
    else:
        print("Empty input! Try again.\n")

# === RESPONSE HANDLING ===
def get_response(user_input, cursor):
    cursor.execute("SELECT question, answer FROM chatbot")
    data = cursor.fetchall()

    if not data:
        return "I'm not trained yet. Please type 'train' to teach me."

    questions = [q for q, _ in data]
    answers = [a for _, a in data]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(questions + [user_input])
    similarity = cosine_similarity(vectors[-1], vectors[:-1])
    best_match_idx = similarity.argmax()
    best_score = similarity[0, best_match_idx]

    if best_score > 0.4:
        return answers[best_match_idx]
    else:
        return "I don't know how to respond to that. Try training me."

# === MAIN LOOP ===
def main():
    conn, cursor = connect_db()
    import_training_data(cursor, conn)
    print("📱 Simple Chatbot (with NLP + SQLite)")
    print("Type 'train' to teach, 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'train':
            train_bot(cursor, conn)
        else:
            response = get_response(user_input, cursor)
            print("Bot:", response)

    conn.close()

# === RUN ===
if __name__ == "__main__":
    main()
