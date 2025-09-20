import sys
import io
from flask import Flask, render_template
from flask_socketio import SocketIO
from dotenv import load_dotenv
from crew import AutopatchCrew
import time
from queue import Queue
import threading

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

log_queue = Queue()

class QueueWriter(io.TextIOBase):
    def __init__(self, old_stdout):
        self.old_stdout = old_stdout
    def write(self, text):
        self.old_stdout.write(text)
        self.old_stdout.flush()
        if text.strip():
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            log_queue.put(f"[{timestamp}] {text.strip()}")
    def flush(self):
        self.old_stdout.flush()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_scan')
def handle_start_scan(json):
    url = json.get('url')
    if not url:
        socketio.emit('log', {'data': 'Error: No URL provided', 'agent': 'system'})
        return
    socketio.emit('log', {'data': f'Received scan request for {url}', 'agent': 'system'})
    socketio.emit('start_loading', {'agent': 'scout'})
    socketio.emit('start_loading', {'agent': 'tester'})

    # Redirect stdout to queue writer
    sys.stdout = QueueWriter(sys.__stdout__)

    def run_crew():
        try:
            print(f"[System] Starting AutopatchCrew for {url}")
            crew = AutopatchCrew(url)
            result = crew.kickoff()
            socketio.emit('log', {'data': '--- SCAN COMPLETE ---', 'agent': 'system'})
            socketio.emit('log', {'data': f'Final Result: {result}', 'agent': 'tester'})
        except Exception as e:
            socketio.emit('log', {'data': f'Error during scan: {str(e)}', 'agent': 'system'})
        finally:
            socketio.emit('end_loading', {'agent': 'scout'})
            socketio.emit('end_loading', {'agent': 'tester'})

    socketio.start_background_task(run_crew)

    def stream_logs():
        while True:
            if not log_queue.empty():
                line = log_queue.get()
                agent = 'scout' if any(kw in line.lower() for kw in ['reconnaissance', 'find_forms', 'scout']) else 'tester'
                socketio.emit('log', {'data': line, 'agent': agent})
            time.sleep(0.01)

    socketio.start_background_task(stream_logs)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
