from flask import Flask
from main import start_bot
from threading import Thread

class ThreadManager:
    def __init__(self):
        self.thread = None
    
    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=start_bot)
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
    
    # thread_manager.start()
    return app