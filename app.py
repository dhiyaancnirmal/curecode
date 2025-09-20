# File: app.py
import sys
import io
from flask import Flask, render_template
from flask_socketio import SocketIO
from dotenv import load_dotenv
from crew import AutopatchCrew

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_scan')
def handle_start_scan(json):
    url = json['url']
    socketio.emit('log', {'data': f'Received scan request for {url}\n'})

    # Redirect stdout to capture logs from CrewAI
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    # Kick off the crew
    crew = AutopatchCrew(url)
    result = crew.kickoff()

    # Restore stdout
    sys.stdout = old_stdout
    
    # Get the captured output
    logs = captured_output.getvalue()
    
    # Send logs and final result to the client
    socketio.emit('log', {'data': logs})
    socketio.emit('log', {'data': f'\n--- SCAN COMPLETE ---\n'})
    socketio.emit('log', {'data': f'Final Result: {result}\n'})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)