from server import Server
import threading

server = Server()

def help_list():
    print("To see the list file of an client: discover <username>")
    print("To check active status of client: ping <username>")

def handle_command():
    while True:
        message = input("Input command: ")

        if "ping" in message:
            # Extract username from the command
            parts = message.split(" ")
            if len(parts) == 2:
                username = parts[1]
                ping_result = server.ping_client(username)
                if ping_result:
                    print(f"{username} is alive.")
                else:
                    print(f"{username} is not responding.")
            else:
                print("Invalid ping command format. Usage: ping <username>")
        elif "discover" in message:
            username = message.split(" ")[-1]
            list_file = server.discover(username)
            if list_file:
                print(f"Files for user {username}: {list_file}")
            else:
                print(f"No files found for user {username} or an error occurred during discovery.")

        elif "end" in message:
            server.status = False
            server.socket.close()
            break

help_list()

thread = threading.Thread(target=handle_command)

thread.daemon = False

thread.start()

server.connect_client()