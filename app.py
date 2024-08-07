from flask import Flask, render_template, request, jsonify
from flask_session import Session
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)

app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

def perform_query_chat(message_history):
    response = client.chat.completions.create(
        model="gpt4",
        messages=message_history,
        temperature=0.7,
        max_tokens=1000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return response

@app.route('/')
def index():
    return render_template('new.html')

message_history = []

@app.route('/chat', methods=['POST'])
def chatbot():
    user_message = request.form.get('user_message').lower()

    # Handle friendly greetings
    greetings = ["hi", "hello", "hey", "hola", "howdy"]
    if user_message in greetings:
        return jsonify({"response": "Hello! How can I assist you with your accounting or tax-related questions today?"})

    if user_message:
        prompt = f"""
         You are "TechEnhance CA Bot", an AI assistant that acts as a chartered accountant.
            User's query:
            {user_message}
           
        """

        message_history.append({"role": "user", "content": prompt})
        response = perform_query_chat(message_history)

        message_history.append({"role": "assistant", "content": response.choices[0].message.content})

        return jsonify({"response": response.choices[0].message.content})

    return jsonify({"response": "Please provide a message!"})

if __name__ == '__main__':
    app.run(debug=True)
