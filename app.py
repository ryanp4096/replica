from flask import Flask
from main import create_client
from threading import Thread

class ThreadManager:
    def __init__(self):
        self.client = None
        self.thread = None
    
    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.client = create_client()
            self.thread = Thread(target=self.client.start_bot)
            self.thread.start()
            print('starting thread')
        else:
            print('thread already started')

def create_app():
    app = Flask(__name__)
    thread_manager = ThreadManager()

    @app.route("/")
    def index():
        thread_manager.start()
        return '<p>Running...</p>'

    return app