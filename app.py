from dotenv import load_dotenv
import os
import json
from flask import Flask, render_template, request
import openai
from waitress import serve

class ChatHistory:
    def __init__(self, hist_path):
        self.hist_path = hist_path

    def _get_filename(self, chatusername):
        return f"{self.hist_path}/{chatusername}.txt"

    def load(self, chatusername):
        filename = self._get_filename(chatusername)
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return json.loads(file.read())
        return []

    def save(self, chatusername, messages):
        filename = self._get_filename(chatusername)
        with open(filename, "w") as file:
            file.write(json.dumps(messages))

load_dotenv()  # Add this line to load environment variables from the .env file

app = Flask(__name__)
openai.api_key = os.getenv('OPEN_API_KEY')
chat_history = ChatHistory(os.getenv('HISTORY_PATH'))

@app.route("/chat", methods=["POST"])
def chat():
    chatusername = request.form["chatusername"]
    userinput = request.form["userinput"]

    messages = chat_history.load(chatusername)
    messages.append({"role": "user", "content": userinput})
    response = send_request(messages)
    messages.append({"role": "assistant", "content": response})
    chat_history.save(chatusername, messages)

    return render_template("index.html", chatusername=chatusername, messages=messages, userinput="")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chatusername="", messages=[], userinput="")

def send_request(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=int(os.getenv('MAX_TOKENS')),
        temperature=float(os.getenv('TEMPERATURE')),
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

    message = response.choices[0].message['content']
    return message.strip()