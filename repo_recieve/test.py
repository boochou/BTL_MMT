import os
import socket
import threading
import json
import time
import hashlib

IP = socket.gethostbyname(socket.gethostname()) #"127.0.0.1" #HOST #loopback
SERVER_PORT = 56789
ADDRESS = (IP, SERVER_PORT)
FORMAT = "UTF-8"

class Client:
    PING_MESSAGE = "PING"
    PONG_MESSAGE = "PONG"
    #start the client
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("---Client side---")
        self.server_status = self.connect_server() #connect to server + set connected status
        self.ping_stop_event = threading.Event() # Event to signal stopping the ping thread
        self.username =''
    #client connect to server
    def connect_server(self):
        try:
            #input IP of server
            print("Enter IP of server to connect: ")
            IP = input()
            ADDRESS = (IP, SERVER_PORT)
            
            self.socket.connect(ADDRESS)
            ipaddr, port = self.socket.getsockname() #get local ip and port of client's socket
            
            #create new socket
            address = (ipaddr, port + 1)
            self.new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.new_socket.bind(address)
            self.new_socket.listen()
        
            print("Client Address:", ipaddr, ",", port)
            print("Client with Server at:", ipaddr, ",", port)
            print("Client Listening At Address:", ipaddr, ",", port + 1)

            #return True
            self.socket.send("CONNECT".encode(FORMAT))
            rev_message = self.socket.recv(1025).decode(FORMAT)
            if rev_message == "RESPONE 200":
                return True
        except Exception as e:
            return False
        
    def publish_file(self, lname, fname, fpath):
        self.socket.send("ASK _PUBLISH".encode(FORMAT))
        #time.sleep(1)
        #check for the permission to publish file
        try:
            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            if mess_from_server == "You can publish file":
                print("File upload is in progress")
            elif mess_from_server == "You can't publish any file":
                print("You are not allow to publish file")
                return False
        except Exception as e:
            print(f"Error to check for the permission publishing file: {e}")
            return False
        #upload file
        try:
            # Check if the file exists in the local file system
            if not os.path.exists(lname):
                print(f"File '{lname}' not found. Cannot publish file.")
                return

            # Check if the client repo directory exists, create it if necessary
            if not os.path.exists(fpath):
                os.makedirs(fpath)

            # Construct the target path in the client repo
            target_path = os.path.join(fpath, fname)

            # Check if the file already exists in the client repo
            if os.path.exists(target_path):
                print(f"File '{fname}' already exists in the client repository. Cannot publish file.")
                return

            # Copy the file from the local file system to the client repo
            with open(lname, 'rb') as source_file, open(target_path, 'wb') as target_file:
                target_file.write(source_file.read())

            print(f"File '{fname}' published successfully to '{fpath}'.")
            
            #send data to server to update database
            to_send = {"username": self.username, "lname": lname, "fname": fname, "fpath": fpath}
            to_send = json.dumps(to_send)
            self.socket.send(to_send.encode(FORMAT))
            return True
    
        except Exception as e:
            print(f"Error during file publishing: {e}")
            return False
    
    def handle_listen(self):
        try:
            while True:
                conn, addr = self.new_socket.accept()
                message = conn.recv(1024).decode(FORMAT)
                if message == self.PING_MESSAGE:
                    conn.send(self.PONG_MESSAGE.encode(FORMAT))
                else:
                    print(f"MESSAGE: {message}")
                    self.send_file(message)
        except Exception as e:
            print(f"Error handling listen: {e}")
    
    def stop_ping_thread(self):
        self.ping_stop_event.set()
        self.new_socket.close()
        
    def log_in(self):
        try:
            self.socket.send("SIGNIN".encode(FORMAT))
            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            username = input(mess_from_server)
            self.socket.send(username.encode(FORMAT))

            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            password = input(mess_from_server)
            #hashed_password = hashlib.sha256(password.encode(FORMAT)).hexdigest()

            self.socket.send(password.encode(FORMAT))

            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            print(str(mess_from_server))

            if mess_from_server == "Login successful.":
                self.server_status = True
                self.username = username
                return True
            else:
                self.server_status = False
                return False
        except Exception as e:
            print(f"Error during login: {e}")
            self.server_status = False
            return False
        
    def sign_up(self):
        try:
            self.socket.send("SIGNUP".encode(FORMAT))
            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            username = input(mess_from_server)
            self.socket.send(username.encode(FORMAT))

            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            password = input(mess_from_server)
            #hashed_password = hashlib.sha256(password.encode(FORMAT)).hexdigest()

            self.socket.send(password.encode(FORMAT))

            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            print(str(mess_from_server))

            if mess_from_server == "Signup successfully.":
                self.server_status = True
                return True
            else:
                self.server_status = False
                return False
        except Exception as e:
            print(f"Error during login: {e}")
            self.server_status = False
            return False

    def send_request(self,file_name, addr):
        print({addr})
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        try:
            s.connect(addr)
            print("Connection successful!")
            default_port = 12346
            local_ip = self.get_local_ip()
            mess = f"REQUEST {file_name} AT {local_ip} {default_port}"
            s.sendall(mess.encode(FORMAT))

            return True
        except socket.error as e:
            print(f"Connection failed: {e}")
            return False

    def get_local_ip(self):
        # Create a socket to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't have to be reachable
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip
    
    def send_file(self, data):
        path = "./repo_publish"
        _, file_path_, _, host, port = data.split(" ")
        port = int(port)
        file_path = os.path.join(path, file_path_)
        s = None  # Initialize the variable outside the try block
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            # Connect to the other peer
        s.connect((host, port))

            # Get the file size
        
        try:
            with open(file_path, 'rb') as file:
                # Start sending the file in chunks
                file_size = os.path.getsize(file_path)
                #print("CUU TUIIIIIIIIIIIIIIIIIIII\n")
            # Send the file size to the other peer
                s.sendall(f"{file_size}\n".encode())
                chunk_size = 1024
                sent_bytes = 0
                while sent_bytes < file_size:
                    # Read a chunk of data from the file
                    bytes_read = file.read(chunk_size)
                    if not bytes_read:
                        # If we've reached the end of the file, break out of the loop
                        break

                    # Send the chunk of data to the other peer
                    s.sendall(bytes_read)

                    # Update progress
                    sent_bytes += len(bytes_read)
        except (FileNotFoundError, IOError) as e:
            if s:
                s.sendall("INVALID_FILEPATH\n".encode(FORMAT))
            print(f"Error: {e}")
        finally:
            if s:
                s.close()

    def receive_file(self, file_name, addr): #ahihi
        dir = "./repo_recieve"
        save_path = os.path.join(dir,file_name)
        host = self.get_local_ip() #addr to listen recieve file
        port = 12346
        #des_ip = input("The selected IP: ")
        #des_port = input("The selected port: ")
        #add = (des_ip,int(des_port))
        check = self.send_request(file_name, addr)
        # Create a TCP socket
        
        if check:          
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Bind the socket to the specified host and port
                s.bind((host, port))

                # Listen for incoming connections
                s.listen()

                print(f"Waiting for a connection on {host}:{port}")

                # Accept a connection from a peer
                conn, addr = s.accept()
                print(f"Connection established with {addr}")

                # Receive the file size
                mess = b""
                file_size_data = b""
                while True:
                    byte = conn.recv(1)
                    print(byte)
                    mess+=byte
                    if byte == b"\n":
                        break
                    file_size_data += byte
                              
                message = mess.decode(FORMAT)
                if message == "INVALID_FILEPATH\n":
                    return False
                print(message)
                file_size = int(file_size_data.decode(FORMAT))

                # Open a file for writing in binary mode
                with open(save_path, 'wb') as file:
                    # Start receiving the file in chunks
                    chunk_size = 1024
                    received_bytes = 0
                    while received_bytes < file_size:
                        # Receive a chunk of data from the other peer
                        bytes_received = conn.recv(chunk_size)
                        if not bytes_received:
                            # If the connection is closed, break out of the loop
                            break

                        # Write the received data to the file
                        file.write(bytes_received)

                        # Update progress
                        received_bytes += len(bytes_received)
                        print(f"Receiving {received_bytes}/{file_size} bytes", end='\r')
            print(f"File '{file_name}' is fetched successfully to '{dir}'.")
            
            #server update database
            self.socket.send("FETCH_SUCCESSFULLY".encode(FORMAT))
            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            to_send = {"username": self.username, "fname": file_name, "fpath": dir}
            to_send = json.dumps(to_send)
            self.socket.send(to_send.encode(FORMAT))
            return True
        else:
            print(f"Can not send the message!!!!")
            return False

    def fetch(self, fname):
        self.socket.send("ASK _FILE".encode(FORMAT))
        try:
            mess_from_server = self.socket.recv(1024).decode(FORMAT)
            username = ''
            ip = ''
            port = ''
            if mess_from_server == "File name to fetch?":
                fname_username = (fname, self.username)
                self.socket.send(json.dumps(fname_username).encode(FORMAT))
                list_clients = self.socket.recv(1024).decode(FORMAT)
                if list_clients == "You cannot fetch existed file!":
                    print(str(list_clients))
                    return "1"
                list_clients = json.loads(list_clients)
                ###
                if list_clients:
                    print(list_clients)
                    usr = input("Choose client you want to fetch file from: ")
                    username = usr
                    for client_info in list_clients:
                        if client_info["username"] == username:
                            ip = client_info["ipaddr"]
                            port = client_info["port"]
                            break
                    addr = (ip, int(port) + 1)
                    if not self.receive_file(fname, addr):
                        print("Failed to fetch ", fname)
                else:
                    print("No clients found with the requested file.")
                    return "3"
        except:
            print("Failed to fetch", fname)
            return "3"
    