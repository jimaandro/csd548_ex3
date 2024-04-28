from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    message = os.getenv("MESSAGE", "Hello from Python Flask!")
    return message

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

