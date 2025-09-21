import sys
import io
import re
from flask import Flask, render_template
from flask_socketio import SocketIO
from dotenv import load_dotenv
from crew import AutopatchCrew
import time
from queue import Queue
from datetime import datetime
from tools.browser_tools import toggle_headless_mode, get_headless_mode

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

log_queue = Queue()

def clean_ansi_codes(text):
    """Remove ANSI escape codes from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def is_meaningful_log(text):
    """Check if log text is meaningful (not just empty or whitespace)"""
    cleaned = clean_ansi_codes(text).strip()
    return len(cleaned) > 0 and not cleaned.isspace()

class QueueWriter(io.TextIOBase):
    def __init__(self, old_stdout):
        self.old_stdout = old_stdout

    def write(self, text):
        self.old_stdout.write(text)
        self.old_stdout.flush()
        # Put the raw, unmodified text into the queue
        log_queue.put(text)

    def flush(self):
        self.old_stdout.flush()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_scan')
def handle_start_scan(json):
    url = json.get('url')
    if not url:
        timestamp = datetime.now().strftime("%H:%M:%S")
        socketio.emit('log', {'data': f'[{timestamp}] Error: No URL provided', 'agent': 'system'})
        return
    
    original_stdout = sys.stdout
    sys.stdout = QueueWriter(sys.__stdout__)

    def run_crew():
        try:
            crew = AutopatchCrew(url)
            result = crew.kickoff()
            timestamp = datetime.now().strftime("%H:%M:%S")
            socketio.emit('log', {'data': f'[{timestamp}] --- SCAN COMPLETE ---', 'agent': 'system'})
            socketio.emit('log', {'data': f'[{timestamp}] Final Result: {result}', 'agent': 'fixer'})
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            socketio.emit('log', {'data': f'[{timestamp}] Error during scan: {str(e)}', 'agent': 'system'})
        finally:
            sys.stdout = original_stdout
            socketio.emit('scan_complete')

    def stream_logs():
        # Track which agents have started working and produced content
        agent_states = {'crawler': False, 'scout': False, 'tester': False, 'fixer': False}
        agent_content = {'crawler': False, 'scout': False, 'tester': False, 'fixer': False}
        
        while True:
            if not log_queue.empty():
                raw_line = log_queue.get()
                
                # Clean ANSI codes and check if meaningful
                cleaned_line = clean_ansi_codes(raw_line).strip()
                if not is_meaningful_log(raw_line):
                    continue
                
                agent = 'system'
                lower_line = cleaned_line.lower()

                # More precise agent detection based on agent names and tool usage
                if any(keyword in lower_line for keyword in [
                    'website crawler', 'crawl website tool', 'crawling', 'visiting:', 
                    'urls discovered', 'site map', 'crawl completed', 'starting crawl', 'total urls',
                    'smart crawl', 'database url pattern', 'pattern limit reached', 'skipping',
                    'dynamic url pattern', 'found database url pattern'
                ]) or re.search(r'found \d+ new links', lower_line):
                    agent = 'crawler'
                    agent_states['crawler'] = True
                    agent_content['crawler'] = True
                elif any(keyword in lower_line for keyword in [
                    'website reconnaissance specialist', 'reconnaissance specialist', 'find forms tool', 
                    'scanning for forms', 'forms found', 'form #', 'no forms found', 'form details',
                    'form html', 'form analysis', 'identifying forms', 'form detection'
                ]):
                    agent = 'scout'
                    agent_states['scout'] = True
                    agent_content['scout'] = True
                elif any(keyword in lower_line for keyword in [
                    'vulnerability tester', 'submit form tool', 'test for xss', 'testing for', 
                    'sql injection', 'xss test', 'penetration test', 'security test', 'vulnerability test',
                    'form fields', 'payload', 'injection', 'xss vulnerability', 'sql vulnerability',
                    'idor test', 'idor vulnerability', 'security config', 'security configuration',
                    'security headers', 'missing header', 'server header', 'content-security-policy'
                ]):
                    agent = 'tester'
                    agent_states['tester'] = True
                    agent_content['tester'] = True
                elif any(keyword in lower_line for keyword in [
                    'vulnerability fixer', 'suggested code fixes', 'code fix', 'patch', 
                    'security fix', 'vulnerability patch', 'fix suggestion', 'code snippet',
                    'parameterized queries', 'input validation', 'sanitization'
                ]):
                    agent = 'fixer'
                    agent_states['fixer'] = True
                    agent_content['fixer'] = True
                elif '--- SCAN COMPLETE ---' in cleaned_line or 'final result:' in lower_line:
                    agent = 'system'
                
                # Add timestamp to the log data
                timestamp = datetime.now().strftime("%H:%M:%S")
                timestamped_data = f"[{timestamp}] {cleaned_line}"
                    
                socketio.emit('log', {'data': timestamped_data, 'agent': agent})
            else:
                # Send thinking states for agents that have started but haven't produced content yet
                timestamp = datetime.now().strftime("%H:%M:%S")
                for agent_name, has_started in agent_states.items():
                    if has_started and not agent_content[agent_name]:
                        socketio.emit('thinking', {'agent': agent_name, 'timestamp': timestamp})
            time.sleep(0.1)

    # Start both background tasks
    socketio.start_background_task(run_crew)
    socketio.start_background_task(stream_logs)

@socketio.on('toggle_headless')
def handle_toggle_headless():
    """Toggle headless mode and return current state"""
    new_state = toggle_headless_mode()
    timestamp = datetime.now().strftime("%H:%M:%S")
    mode_text = "headless" if new_state else "visible browser"
    socketio.emit('log', {'data': f'[{timestamp}] Browser mode changed to: {mode_text}', 'agent': 'system'})
    socketio.emit('headless_toggled', {'headless': new_state})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5002, allow_unsafe_werkzeug=True)

