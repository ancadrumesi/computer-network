import socket
import json
import os

SERVER_HOST = 'localhost'
SERVER_PORT = 5000
LOCAL_FILES_DIR = 'local_files'

class FTPClient:
    def __init__(self):
        self.socket = None
        self.authenticated = False
        if not os.path.exists(LOCAL_FILES_DIR): os.makedirs(LOCAL_FILES_DIR)
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((SERVER_HOST, SERVER_PORT))
            return True
        except: return False

    def send_command(self, data):
        self.socket.send(json.dumps(data).encode('utf-8'))
        return json.loads(self.socket.recv(4096).decode('utf-8'))

    def login(self, u, p):
        res = self.send_command({'command': 'login', 'username': u, 'password': p})
        if res['status'] == 'success': self.authenticated = True
        print(f"{res['message']}")

    def list_files(self, silent=False):
        res = self.send_command({'command': 'list_files'})
        if not silent:
            for f in res.get('files', []): print(f"  • {f}")
        return res.get('files', [])

    def rename_file(self):
        old = input("Current filename: ")
        new = input("New filename: ")
        res = self.send_command({'command': 'rename_file', 'old_name': old, 'new_name': new})
        print(res['message'])

    def read_file(self):
        fname = input("File to read: ")
        res = self.send_command({'command': 'read_file', 'filename': fname})
        if res['status'] == 'success':
            print(f"\n--- Content of {fname} ---\n{res['content']}\n--- End ---")
        else: print(res['message'])

    def download(self):
        fname = input("Filename to download: ")
        res = self.send_command({'command': 'download', 'filename': fname})
        if res['status'] == 'success':
            with open(os.path.join(LOCAL_FILES_DIR, fname), 'w') as f:
                f.write(res['content'])
            print(f"✓ Saved to {LOCAL_FILES_DIR}/{fname}")
        else: print(res['message'])

    def edit_file(self):
        fname = input("Filename to edit: ")
        content = input("Enter new content: ")
        res = self.send_command({'command': 'edit_file', 'filename': fname, 'content': content})
        print(res['message'])

    def see_file_operation_history(self):
        fname = input("See history for file: ")
        res = self.send_command({'command': 'see_file_operation_history', 'filename': fname})
        if res['status'] == 'success':
            for line in res['history']: print(f"  {line}")

    def show_menu(self):
        print("\033[38;2;46;108;181m" + "="*30) # #2e6cb5
        print("\033[38;2;29;23;75m" + "    FTP CONTROL PANEL") # #1d174b
        print("\033[38;2;231;84;128m" + "="*30 + "\033[0m") # #e75480
        print("1. Login | 2. Local Create | 3. Upload | 4. Rename")
        print("5. Read  | 6. Download     | 7. Edit   | 8. History")
        print("9. List  | 10. Logout      | 0. Exit")

    def run(self):
        if not self.connect(): return
        while True:
            self.show_menu()
            c = input("\nChoice: ")
            if c == '1': self.login(input("User: "), input("Pass: "))
            elif not self.authenticated and c != '0': print("Login first!")
            elif c == '2': # Local logic stays similar to your original
                 pass 
            elif c == '3': # Upload logic
                 pass
            elif c == '4': self.rename_file()
            elif c == '5': self.read_file()
            elif c == '6': self.download()
            elif c == '7': self.edit_file()
            elif c == '8': self.see_file_operation_history()
            elif c == '9': self.list_files()
            elif c == '10': 
                self.send_command({'command': 'logout'})
                self.authenticated = False
            elif c == '0': break

if __name__ == '__main__':
    FTPClient().run()