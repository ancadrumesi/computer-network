import socket
import json
import os
import threading
from datetime import datetime

# Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
FILES_DIR = 'files'
DEFAULT_USER = 'student'
DEFAULT_PASSWORD = '1234'

file_history = {}

def log_event(filename, event):
    """Logs an operation for a specific file"""
    if filename not in file_history:
        file_history[filename] = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_history[filename].append(f"[{timestamp}] {event}")

def ensure_files_dir():
    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)

def authenticate(username, password):
    return username == DEFAULT_USER and password == DEFAULT_PASSWORD

def handle_client(conn, addr):
    print(f"\n🔗 Client connected from {addr}")
    authenticated = False
    current_user = None
    
    try:
        while True:
            request_data = conn.recv(4096).decode('utf-8')
            if not request_data: break
            
            try:
                request = json.loads(request_data)
                command = request.get('command')
                response = {'status': 'error', 'message': 'Unknown command'}

                if command == 'login':
                    if authenticate(request.get('username'), request.get('password')):
                        authenticated, current_user = True, request.get('username')
                        response = {'status': 'success', 'message': f'Welcome {current_user}!'}
                    else:
                        response = {'status': 'error', 'message': 'Invalid credentials'}
                
                elif not authenticated:
                    response = {'status': 'error', 'message': 'Not authenticated'}
                
                # --- File Operations ---
                elif command == 'list_files':
                    response = {'status': 'success', 'files': os.listdir(FILES_DIR)}

                elif command == 'create_file' or command == 'upload':
                    fname, content = request.get('filename'), request.get('content', '')
                    with open(os.path.join(FILES_DIR, fname), 'w') as f:
                        f.write(content)
                    log_event(fname, f"Created/Uploaded by {current_user}")
                    response = {'status': 'success', 'message': f'File {fname} saved'}

                elif command == 'rename_file':
                    old, new = request.get('old_name'), request.get('new_name')
                    os.rename(os.path.join(FILES_DIR, old), os.path.join(FILES_DIR, new))
                    log_event(old, f"Renamed to {new}")
                    # Transfer history to new name
                    if old in file_history:
                        file_history[new] = file_history.pop(old)
                    response = {'status': 'success', 'message': f'Renamed {old} to {new}'}

                elif command in ['read_file', 'download']:
                    fname = request.get('filename')
                    with open(os.path.join(FILES_DIR, fname), 'r') as f:
                        content = f.read()
                    response = {'status': 'success', 'content': content}

                elif command == 'edit_file':
                    fname, content = request.get('filename'), request.get('content')
                    with open(os.path.join(FILES_DIR, fname), 'w') as f:
                        f.write(content)
                    log_event(fname, f"Edited by {current_user}")
                    response = {'status': 'success', 'message': 'File updated'}

                elif command == 'see_file_operation_history':
                    fname = request.get('filename')
                    history = file_history.get(fname, ["No history available."])
                    response = {'status': 'success', 'history': history}

                elif command == 'logout':
                    authenticated = False
                    response = {'status': 'success', 'message': 'Logged out'}
                
            except Exception as e:
                response = {'status': 'error', 'message': str(e)}
            
            conn.send(json.dumps(response).encode('utf-8'))
    finally:
        conn.close()

def start_server():
    ensure_files_dir()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"🚀 FTP Server active on {SERVER_PORT}...")
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    start_server()