import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

DB_NAME = 'chatbot.db'

class ChatBot(BoxLayout):
    def __init__(self, **kwargs):
        super(ChatBot, self).__init__(orientation='vertical', **kwargs)
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.init_db()

        self.chat_log = Label(size_hint_y=8, text='Hello! Type something below...', halign='left', valign='top')
        self.chat_log.bind(size=self.chat_log.setter('text_size'))

        self.input_box = TextInput(size_hint_y=1, multiline=False)
        self.send_button = Button(text='Send', size_hint_y=1)
        self.send_button.bind(on_press=self.respond)

        self.add_widget(self.chat_log)
        self.add_widget(self.input_box)
        self.add_widget(self.send_button)

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot (
                question TEXT PRIMARY KEY,
                answer TEXT NOT NULL
            )
        """)
        self.conn.commit()
        self.import_data()

    def import_data(self, filename='chatbot_training_data.txt'):
        if not os.path.exists(filename):
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
                    self.cursor.execute("INSERT OR REPLACE INTO chatbot (question, answer) VALUES (?, ?)", (question, answer))
                    question, answer = None, None
        self.conn.commit()

    def get_response(self, user_input):
        self.cursor.execute("SELECT question, answer FROM chatbot")
        data = self.cursor.fetchall()
        if not data:
            return "I'm not trained yet."
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
            return "I don't understand that yet."

    def respond(self, instance):
        user_input = self.input_box.text.strip()
        if not user_input:
            return
        response = self.get_response(user_input)
        self.chat_log.text += f"\nYou: {user_input}\nBot: {response}"
        self.input_box.text = ''

class ChatBotApp(App):
    def build(self):
        return ChatBot()

if __name__ == '__main__':
    ChatBotApp().run()
