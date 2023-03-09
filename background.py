from flask import Flask
from threading import Thread

flask_app = Flask('')


@flask_app.route('/')
def home():
    return "flask running.."


def run():
    flask_app.run(host='0.0.0.0', port=80)


def non_stop():
    t = Thread(target=run)
    t.start()
