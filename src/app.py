#!/usr/bin/env python3
"""
Flask application for streaming terminal sessions to web clients.
Windows-compatible version using subprocess instead of PTY.
Provides real-time bidirectional communication with terminal stdin/stdout.
"""

import os
import sys
import subprocess
import threading
import queue
import json
import platform
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active terminal sessions
terminal_sessions = {}

# Detect platform
IS_WINDOWS = platform.system() == 'Windows'


class TerminalSession:
    """Manages a terminal session (cross-platform: Windows/Unix)."""
    
    def __init__(self, session_id, shell=None):
        self.session_id = session_id
        
        # Set shell based on platform
        if shell is None:
            if IS_WINDOWS:
                self.shell = 'cmd.exe'
            else:
                self.shell = '/bin/bash'
        else:
            self.shell = shell
            
        self.process = None
        self.stdin_thread = None
        self.stdout_thread = None
        self.running = False
        self.input_queue = queue.Queue()
        
    def start(self):
        """Start a new terminal session."""
        try:
            # Create the subprocess
            if IS_WINDOWS:
                # Windows: use cmd.exe with pipes
                self.process = subprocess.Popen(
                    self.shell,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=0,
                    text=False,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0
                )
            else:
                # Unix: use bash with pipes (no PTY, but still works)
                self.process = subprocess.Popen(
                    self.shell,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=0,
                    text=False,
                    shell=True
                )
            
            self.running = True
            
            # Start threads to handle I/O
            self.stdout_thread = threading.Thread(target=self._read_output, daemon=True)
            self.stdin_thread = threading.Thread(target=self._write_input, daemon=True)
            self.stdout_thread.start()
            self.stdin_thread.start()
            
            logger.info(f"Terminal session {self.session_id} started with PID {self.process.pid}")
            
        except Exception as e:
            logger.error(f"Failed to start terminal session: {e}")
            self.running = False
            
    def _read_output(self):
        """Read output from terminal and emit to all connected clients."""
        try:
            while self.running and self.process and self.process.poll() is None:
                try:
                    # Read from stdout with timeout
                    data = self.process.stdout.read(4096)
                    if data:
                        # Emit to all clients in this session
                        socketio.emit('terminal_output', {
                            'data': data.decode('utf-8', errors='replace')
                        }, room=self.session_id)
                    else:
                        # Process ended
                        break
                except Exception as e:
                    logger.error(f"Error reading from terminal: {e}")
                    break
                    
            # Process has ended
            if self.running:
                self.running = False
                socketio.emit('terminal_exited', {'code': self.process.returncode}, room=self.session_id)
                
        except Exception as e:
            logger.error(f"Fatal error in read_output: {e}")
            self.running = False
            
    def _write_input(self):
        """Write input from queue to terminal stdin."""
        try:
            while self.running:
                try:
                    # Get input from queue with timeout
                    data = self.input_queue.get(timeout=0.1)
                    if data is not None and self.process and self.process.stdin:
                        self.process.stdin.write(data.encode('utf-8'))
                        self.process.stdin.flush()
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error writing to terminal: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Fatal error in write_input: {e}")
            
    def write(self, data):
        """Queue data to be written to terminal stdin."""
        if self.running:
            self.input_queue.put(data)
            
    def resize(self, rows, cols):
        """Resize terminal (Windows doesn't support this, but we acknowledge it)."""
        # Windows doesn't support terminal resizing via subprocess
        # This is a limitation of Windows command prompt
        if not IS_WINDOWS:
            try:
                import fcntl
                import struct
                # This would only work with PTY on Unix
                pass
            except Exception as e:
                logger.debug(f"Terminal resize not supported: {e}")
                
    def terminate(self):
        """Terminate the terminal session."""
        self.running = False
        if self.process:
            try:
                if IS_WINDOWS:
                    # Windows: use taskkill or terminate
                    self.process.terminate()
                else:
                    # Unix: send SIGTERM
                    self.process.terminate()
                    
                # Wait for process to end
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                # Force kill if terminate doesn't work
                try:
                    self.process.kill()
                except:
                    pass
            except Exception as e:
                logger.error(f"Error terminating process: {e}")


@app.route('/')
def index():
    """Serve the main terminal page."""
    return render_template('terminal.html')


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    emit('response', {'data': f'Connected to terminal server ({platform.system()})'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")
    # Clean up session if it exists
    session_id = f"session_{request.sid}"
    if session_id in terminal_sessions:
        terminal_sessions[session_id].terminate()
        del terminal_sessions[session_id]


@socketio.on('init_terminal')
def handle_init_terminal(data):
    """Initialize a new terminal session."""
    session_id = f"session_{request.sid}"
    shell = data.get('shell', None)
    
    if session_id not in terminal_sessions:
        session = TerminalSession(session_id, shell)
        session.start()
        terminal_sessions[session_id] = session
        join_room(session_id)
        emit('terminal_initialized', {'session_id': session_id, 'platform': platform.system()})
        logger.info(f"Terminal initialized for session {session_id}")


@socketio.on('terminal_input')
def handle_terminal_input(data):
    """Handle terminal input from client."""
    session_id = f"session_{request.sid}"
    
    if session_id in terminal_sessions:
        session = terminal_sessions[session_id]
        input_data = data.get('data', '')

        # Logic to switch to a python session
        if session.shell != 'python3 -i -u' and input_data.strip() == 'python3':
            logger.info(f"Switching to Python session for {session_id}")
            session.terminate()
            
            new_session = TerminalSession(session_id, shell='python3 -i -u')
            new_session.start()
            terminal_sessions[session_id] = new_session
            socketio.emit('terminal_initialized', {'session_id': session_id, 'platform': platform.system()}, room=session_id)
            return

        # Logic to exit a python session and return to a default shell
        if session.shell == 'python3 -i -u' and input_data.strip() in ['quit()', 'exit()']:
            logger.info(f"Exiting Python session for {session_id}, returning to default shell.")
            session.terminate()

            new_session = TerminalSession(session_id) # Default shell
            new_session.start()
            terminal_sessions[session_id] = new_session
            socketio.emit('terminal_initialized', {'session_id': session_id, 'platform': platform.system()}, room=session_id)
            return

        session.write(input_data)


@socketio.on('terminal_resize')
def handle_terminal_resize(data):
    """Handle terminal resize."""
    session_id = f"session_{request.sid}"
    
    if session_id in terminal_sessions:
        rows = data.get('rows', 24)
        cols = data.get('cols', 80)
        terminal_sessions[session_id].resize(rows, cols)


if __name__ == '__main__':
    print(f"🖥️  Running on {platform.system()}")
    print("📱 Flask Terminal Server")
    print("🌐 Open http://localhost:5000 in your browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
