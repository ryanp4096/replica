from flask import Flask
from main import create_client
from threading import Thread
from datetime import datetime, timedelta

class ThreadManager:
    def __init__(self):
        self.client = None
        self.thread = None
        self.closed = False
        self.created = datetime.now()
    
    def start(self):
        if self.closed:
            print('server closed')
            return
        if self.thread is None or not self.thread.is_alive():
            if self.closed:
                print('server closed')
                return
            self.client = create_client()
            self.thread = Thread(target=self.client.start_bot)
            self.thread.start()
            print('starting thread')
        else:
            print('thread already started')
    
    def close(self):
        if (datetime.now() - self.created) < timedelta(minutes=5):
            print('too early to close')
            return
        self.closed = True
        print('closing')
        self.client.close()

def create_app():
    app = Flask(__name__)
    thread_manager = ThreadManager()

    @app.route("/")
    def index():
        thread_manager.start()
        return '<p>Running...</p>'
    
    @app.route("/restart")
    def restart():
        thread_manager.close()
        return '<p>Closing...</p>'

    return app