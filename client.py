'''
PAWPRINT : rjy7wb
5/1/2019

Description:
client Login sends messages to server, and receives responses.
'''



import sys
import socket
import time

host = '127.0.0.1'
port = 17990

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print('Chat Client V1')
    try:
        while True:
            message = raw_input('>')
            sock.send(message.encode())
            printme = sock.recv(1024)
            time.sleep(2)
            printme = printme.decode()
            print(printme)
            if printme == '>Server: Connection closed':
                break
    except KeyboardInterrupt:
        print("exiting")
   

