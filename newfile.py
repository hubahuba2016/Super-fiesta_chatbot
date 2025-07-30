import json
import os

# Load or initialize training data
def load_data(filename='chatbot_data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_data(data, filename='chatbot_data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Find a response to the user's input
def get_response(user_input, data):
    return data.get(user_input.lower(), "I don't know how to respond yet.")

# Train the bot by adding a new pair
def train_bot(data):
    question = input("Enter the question: ").strip().lower()
    answer = input("Enter the answer: ").strip()
    data[question] = answer
    print("Training data added.")

# Main loop
def main():
    data = load_data()
    print("Simple Chatbot — type 'train' to teach me, 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'train':
            train_bot(data)
            save_data(data)
        else:
            response = get_response(user_input, data)
            print("Bot:", response)

    save_data(data)
    print("Bye!")

if __name__ == "__main__":
    main()