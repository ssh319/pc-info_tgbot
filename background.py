from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "flask test"


def run():
    app.run(host='0.0.0.0', port=80)


def non_stop():
    t = Thread(target=run)
    t.start()
