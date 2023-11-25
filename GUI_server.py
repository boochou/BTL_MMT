import tkinter as tk
from server import Server
import threading

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server GUI")
        self.server = Server()

        self.status_label = tk.Label(root, text="Server Status: Not Started")
        self.status_label.pack()

        self.clients_label = tk.Label(root, text="Connected Clients:")
        self.clients_label.pack()

        self.log_text = tk.Text(root, height=10, width=50)
        self.log_text.pack()

        self.start_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack()

        self.ping_button = tk.Button(root, text="Ping Clients", command=self.ping_clients, state=tk.DISABLED)
        self.ping_button.pack()

        self.discover_button = tk.Button(root, text="Discover Files", command=self.discover_files, state=tk.DISABLED)
        self.discover_button.pack()

    def start_server(self):
        self.server_thread = threading.Thread(target=self.server.connect_client)
        self.server_thread.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.ping_button.config(state=tk.NORMAL)
        self.discover_button.config(state=tk.NORMAL)
        self.status_label.config(text="Server Status: Running")

        # Start a thread for updating connected clients
        self.update_clients_thread = threading.Thread(target=self.update_clients)
        self.update_clients_thread.start()

    def stop_server(self):
        self.server.status = False
        self.server.socket.close()
        self.server_thread.join()
        self.update_clients_thread.join()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.ping_button.config(state=tk.DISABLED)
        self.discover_button.config(state=tk.DISABLED)
        self.status_label.config(text="Server Status: Stopped")

    def update_clients(self):
        while self.server.status:
            clients = self.server.get_clients()
            clients_str = "\n".join(clients)
            self.clients_label.config(text=f"Connected Clients:\n{clients_str}")
            self.root.update()
            self.root.after(1000)  # Update every 1 second

    def ping_clients(self):
        self.server.ping_all_clients()

    def discover_files(self):
        # Add your logic for file discovery here
        pass

if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()
