# Python program to implement server side of chat room. 
import socket 
import select 
import sys 
from thread import *

  
def clientthread(username,password,conn, addr): 
  
    conn.send("Welcome to this chatroom!") 
    thisUser = None
    password = None
    while True: 
            try: 
                message = conn.recv(2048) 
                if message: 
                    thisUser, password, list_of_users, message = processInput(thisUser, password, list_of_users, addr[0], message)
  
                    message_to_send = "<" + username + "> " + message 
                    broadcast(message, conn) 
  
                else: 
                    remove(conn) 
  
            except: 
                continue
  
def broadcast(message, connection): 
    for clients in list_of_clients: 
        if clients!=connection: 
            try: 
                clients.send(message) 
            except: 
                clients.close() 
  
                # if the link is broken, we remove the client 
                remove(clients) 
  
def remove(connection): 
    if connection in list_of_clients: 
        list_of_clients.remove(connection) 

def processInput(username, password, userList, address, rawmessage):
    message = rawmessage.split()
    
    command = message.pop()
    
    if(username == None):
        if(command == 'login'):
            username = splitMessage.pop()
            password = splitMessage.pop()
            loginCheck = loginNow(username,password)
            if(loginCheck == True):
                userList.append('username')
                message = "<Server> : " ++ username ++ " joins"
                return username,password,userList, message
            
            elif(loginCheck == False):
                message = "<Server> : " ++ "Error invalid credentials"
                return None, None, userList, message
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
        if(command == 'newuser'):
            username = message.pop()
            password = message.pop()
            if(username not in userList):
                username, password, userList = createUser(username,password,userList)
                message = "<Server> : " ++ "creation successful Please Login!"
                return None, None, userList, message
            else:
                message = "<Server> : " ++ "Error account exists"
                return None, None, userList, message
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    else: #UserName has a value
        if(command == 'login' or command == 'newuser'):
            message = "<Server> : " ++"Error, you are already logged in"
            return username, password, userList, message
        elif(command == 'send'):
            message = "<" ++ username ++ ">" ++ message
            return username, password, userList, message
        elif(command == 'logout'):
            message = "<Server> : " ++ username ++ " has logged out"
            userList.remove(username)
            return None, None, userList, message

def loadLogins(filename): # STRING -> [(STRING,STRING)] 
    file = open(filename,'r')
    text = file.read()
    userandpass = text.split()
    LoginTable = []
    
    for x in userandpass:
        y = x.split(',')
        a, b = y[0], y[1]
        LoginTable.append((a,b))
    return LoginTable 

 
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  
if len(sys.argv) != 3: 
    print "Correct usage: script, IP address, port number"
    exit() 
  
IP_address = str(sys.argv[1]) 
  
Port = int(sys.argv[2]) 
  
server.bind((IP_address, Port)) 
  
server.listen(100) 
  
list_of_clients = []
list_of_users = []
list_of_users = loadLogins("logins.txt")


while True: 
  
    conn, addr = server.accept() 
  
    print addr[0] + " connected"
  
    start_new_thread(clientthread,(None,None,conn,addr))     
  
conn.close() 
server.close() 

