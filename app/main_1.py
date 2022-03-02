from flask import Flask
import os
import time


app = Flask(__name__)

@app.route("/")
def hello():

    return os.environ["MUTEX"]

if __name__ == "__main__":
    app.run(host='0.0.0.0', port= 5001)