from client import Client
import threading
FORMAT = "UTF-8"


check_log_in = False

client = Client()
try:#ahihi
    while True:
        print("You need to login first (1). \nIf you don't have account: singup first (2).")
        choice = input("Choose option (1) or (2): ")
        if choice == "1":
            check_log_in = client.log_in()
            if not check_log_in:
                continue
            else: 
                break
        elif choice == "2":
            check_sign_up = client.sign_up()
            if not check_sign_up:
                continue
            print("Now you can login.")
            check_log_in = client.log_in()
            if not check_log_in:
                continue
            else: 
                break
        else: #ahihi coi lại cho người ta lựa chọn khác ik
            # client.server_status = False # update this code
            print("!!!Invalid option!!!")
            print("Please choose valid options: (1) or (2)")
            continue
except KeyboardInterrupt:
    print("\n---Start to disconnect server---")
    client.server_status = False
    client.new_socket.close()
    client.stop_ping_thread()  # Stop the ping thread before exiting

def help_list():

    print("To publish a file: publish <localfile> <filenameinrepo> <pathfileinrepo>")
    print("To download a file: fetch <filename>")
    print("To disconnect server: end")
    
def handle_command():
    try:
        while True:
            if client.server_status:
                try:
                    message = input("Input command: ")
                except EOFError:
                    # Ctrl+C was pressed, break out of the loop
                    print("\n---Start to disconnect server---")
                    client.server_status = False
                    client.new_socket.close()
                    client.stop_ping_thread()  
                    break
                if "publish" in message:
                    parts = message.split(" ")
                    if len(parts) == 4:
                        lname = parts[1]
                        fname = parts[2]
                        fpath = parts[3]
                    else:
                        print("Please enter the correct syntax!")
                        continue
                    result = client.publish_file(lname, fname, fpath)                   
                    if result:
                        print("Publish successful.")
                    else:
                        print("Publish fail.")
                elif "fetch" in message:
                    parts = message.split(" ")
                    if len(parts) != 2:
                        print("Please enter the correct syntax!")
                        continue
                    fname = message.split(" ")[-1]
                    if not fname:
                        print("Please enter the correct syntax!")
                        continue
                    result = client.fetch(fname)
                    if result == "1":
                        print("File in your local.")
                    elif result == "3":
                        print("Process error.")
                    #else:
                        #print("Download successful!")
                elif "end" in message:
                    client.server_status = False
                    client.new_socket.close()
                    client.stop_ping_thread()  # Stop the ping thread before exiting
                    break
                else:
                    print("Please enter the correct syntax!")
                    continue
            else:
                #client.server_status = False
                #client.new_socket.close()
                print("Can't connect to the server !!!")
                break
    except KeyboardInterrupt: #ahihi
        print("\n---Start to disconnect server---")
        client.server_status = False
        client.new_socket.close()
        client.stop_ping_thread()  # Stop the ping thread before exiting

if check_log_in: #ahihi
    help_list()

if check_log_in:
# Start the handle_command thread
    thread_command = threading.Thread(target=handle_command)
    thread_command.daemon = False
    thread_command.start()

    # Start the handle_ping thread
    thread_ping = threading.Thread(target=client.handle_listen)
    thread_ping.daemon = False
    thread_ping.start()

    #Wait for both threads to finish
    thread_command.join()
    thread_ping.join()



