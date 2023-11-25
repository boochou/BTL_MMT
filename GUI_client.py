import tkinter as tk
from client import Client
import threading

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client GUI")
        self.client = Client()

        self.ip_label = tk.Label(root, text="Server IP:")
        self.ip_label.pack()

        self.ip_entry = tk.Entry(root)
        self.ip_entry.pack()

        self.connect_button = tk.Button(root, text="Connect to Server", command=self.connect_to_server)
        self.connect_button.pack()

        self.disconnect_button = tk.Button(root, text="Disconnect from Server", command=self.disconnect_from_server, state=tk.DISABLED)
        self.disconnect_button.pack()

        self.log_text = tk.Text(root, height=10, width=50)
        self.log_text.pack()

        self.upload_button = tk.Button(root, text="Upload File", command=self.upload_file, state=tk.DISABLED)
        self.upload_button.pack()

        self.stop_button = tk.Button(root, text="Stop Client", command=self.stop_client, state=tk.DISABLED)
        self.stop_button.pack()

    def connect_to_server(self):
        server_ip = self.ip_entry.get()
        if server_ip:
            self.client.connect_server(server_ip)
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.upload_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)

    def disconnect_from_server(self):
        self.client.disconnect_from_server()
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.upload_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)

    def upload_file(self):
        # Add your logic for file upload here
        pass

    def stop_client(self):
        self.client.server_status = False
        self.client.new_socket.close()
        self.client.stop_ping_thread()
        self.disconnect_from_server()

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = ClientGUI(root)
    root.mainloop()
