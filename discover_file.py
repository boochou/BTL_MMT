from server import Server
import threading

server = Server()
fname = 'abc.txt'
list = server.discover_file(fname)
print(list)