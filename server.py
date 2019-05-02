'''
PAWPRINT : rjy7wb
5/1/2019

Description:
Server Login receives input from clients, and interprets those commands.
a well written program explains itself +40 amirite?
'''

import sys
import socket
from thread import *

host = '127.0.0.1'
port = 17990
user_info = {}
isClientLoggedIn = False
login_name = ''
name = 'Server'
list_of_clients = []

def userThread(conn,addr):
    while True:
        try:
            message = conn.recv(1024)
            if message:
                ret_message = processMessage(message)
                broadcast(ret_message,conn)
            else:
                remove(conn)
        except Exception as e:
            print(e)
            continue


def broadcast(message,connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.send(message)
            except:
                clients.close()
                remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

def login(message):
    output = ''

    if isClientLoggedIn is True:
        print('Already logged in!')
        return '>Server: Already logged in!'
    if len(message) != 3:
        print('Invalid attempt at login!')
        return '>Server: incorrect usage, correct usage is " login userid password "'
    inputid = message[1]
    provided_pass = message[2]

    if inputid in user_info.keys():

        if provided_pass == user_info[inputid]:
            print('Successful login')
            change_login(inputid)
            output = '>Server: ' + login_name + ' joins'
        else:
            print('Incorrect login')
            output = '>Server: Incorrect login'
    else:
        print('Incorrect login')
        output = '>Server: Incorrect login'
    return output

def newuser(message):
    if len(message) != 3:
        print('Invalid attempt at user creation!')
        return '>Server: incorrect syntax. Correct syntax is: newuser [UserID] [Password]'
    inputid = message[1]
    provided_pass = message[2]
    if inputid in user_info.keys():
        print("User already exists")
        return '>Server: Username already taken, please choose another or login to continue'
    if len(inputid) >= 32:
        print('Username length invalid.')
        return '>Server: Please create a username less than 32 characters'
    if len(provided_pass) < 4 or len(provided_pass) > 8:
        print('Invalid password length')
        return '>Server: Invalid password length'
    user_info[inputid] = provided_pass
    f = open('users.txt', 'a')
    f.write('\n' + inputid + ',' + provided_pass)
    f.close()
    if isClientLoggedIn == False:
        print('New User Created. Please login.')
        appended = 'Please login.'
    else:
        print('New User Created.')
        appended = ''
    return '>Server: New User Created.' + appended

def change_login(user_id):
    global isClientLoggedIn
    global login_name
    output = ''
    if isClientLoggedIn == True:
        print('Connection closed')
        output = '>Server: Connection closed'
        isClientLoggedIn = False
    else:
        isClientLoggedIn = True
    login_name = user_id
    return output   

def logout(message):
    output = '>Server: Connection closed'
    if isClientLoggedIn is True:
        output = change_login('')
    return output

def send(message):
    if isClientLoggedIn is False:
        print('Denied. Please login first.  ')
        return '>Server: Denied. Please login first.'
    message = ' '.join(message)
    message = message[4:]
    message = ('>' + login_name + ':' + message)
    print(message)
    return message

def processMessage(message):
    outputs = str(message).split(' ')
    command = outputs[0]
    function_calls = {
        'login' : login,
        'logout' : logout,
        'send' : send,
        'newuser' : newuser
    }
    if command in function_calls.keys():
        st = function_calls[command](outputs)
    else:
        print('Invalid command')
        st = '>Server: Invalid command'
    return st


if __name__ == '__main__':
    file = open('logins.txt', 'r')
    for line in file:
        line = line.strip('\n')
        info = line.split(',')
        user_info[info[0]] = info[1]
    file.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(3)
    while True:

  
        #print('listening on', (host, port))
        #print('Waiting for connection')
        connection, addr = sock.accept()
        print("Received connection from ", addr[0], "(", addr[1], ")\n")
        list_of_clients.append(connection)
        start_new_thread(userThread,(connection,addr))