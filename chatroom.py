#  rjy7wb - Lab3 Version 2

import sys
import argparse
import json
import re
import socket
import threading

basepatterns = [re.compile(p) for p in ['login',
									'newuser']]

class ClientConnection(threading.Thread):
	def __init__(self, parent, socket, address):
		threading.Thread.__init__(self)
		self.parent = parent
		self.socket = socket
		self.address = address
		self.userid = ""
    

	def run(self):
		print("[server] New client connection from {0}.".format(self.address))
        
		self.send("Lab3 Version 2")
		
		self.loggedIn = False
		pattern = re.compile("(?P<command>login|newuser) (?P<username>\w*) (?P<password>\w*)")
		while not self.loggedIn:
			loginResponse = self.receive()
			match = pattern.match(loginResponse)
			if not match: # NO MATCH
				self.send(loginResponse + " is Invalid. Please try again.")
				continue
			else:
				command = match.group('command')
				userid = match.group('username')
				password = match.group('password')
			uidList = []
			for user in self.parent.users:
				uidList.append(user['userid'])

			if command == "login":
				if self.parent.isLoggedIn(userid):
					self.send("You are Logged In <" + userid + ">")
					continue
				if userid in uidList:
					for user in self.parent.users:
						if userid == user['userid'] and password == user['password'] and not self.parent.isLoggedIn(userid):
							self.send("Success! Hello, {0}!".format(user['userid']))
							self.userid = user['userid']
							self.loggedIn = True
					if not self.loggedIn: self.send("Invalid password.")						
				else:
					self.send("Invalid UserID")
			elif command == "newuser":
				if match.group('username') in uidList: 
					self.send(" username exists")
				elif len(match.group('username')) > 32: # 32 char limit
					self.send(" The length of the UserID should be less than 32")
				elif len(match.group('password')) not in range(4,8): # 4 - 8 limit
					self.send("The length of the Password should be between 4 and 8 characters")
				else: # Otherwise accept the user as they successfull signed up
					self.userid = match.group('username')
					self.parent.addUser(match.group('username'), match.group('password'))
					self.send("Hello, {0}!".format(self.userid))
					self.loggedIn = True
					continue

		print("[server] {0}, Welcome!".format(self.userid))
		self.parent.login(self.userid, self)

		pattern = re.compile("(?P<command>send|who|logout) ?(?P<args>.*)?")
		sendPattern = re.compile("(?P<recepient>\w*) (?P<message>.*)")
		while True:
			msg = self.receive()
			match = pattern.match(msg)
			if not match:
				self.send("Unknown command. Please try again.")
				continue
			if match.group('command') == "who": # Check to see other clients in the chatroom
				uidList = []
				for conn in self.parent.activeConnections:
					uidList.append(conn[0])
				self.send("{0} in the chatroom right now: {1}".format(len(uidList), ", ".join(uidList)))
			elif match.group('command') == "send": # Send to either all clients or one
				sendMatch = sendPattern.match(match.group('args'))
				if not sendMatch:
					self.send(command + "is Invalid. Please try again.")
					continue
				elif sendMatch.group('recepient') == "all":
					self.parent.sendToAll(self.userid, sendMatch.group('message'))
				else:
					sent = False
					for conn in self.parent.activeConnections:
						if conn[0] == sendMatch.group('recepient'):
							self.parent.sendToUser(self.userid, sendMatch.group('recepient'), sendMatch.group('message'))
							sent = True
					if not sent: self.send("Invalid UserID".format(sendMatch.group('recepient')))
			elif match.group('command') == "logout": # User wants to logout
				self.send("Goodbye.")
				break
		print("[server] {0} LoggedOut".format(self.address))
		self.exit()
    

	def send(self, msg):
		msg += ('\n')
		self.socket.send('{payload: <{maxlen}}'.format(payload=msg, maxlen=1024).encode('utf-8'))

	def receive(self):
		msg = b""
		while len(msg) < 1024:
			msg += self.socket.recv(1024 - len(msg))
		return msg.decode('utf-8').split('\n', 1)[0]

	def exit(self):
		self.socket.close()
		self.parent.logOut(self.userid)

class Server():
	def __init__(self, configPath):
		self.error = False
		self.run = True
		self.activeConnections = []
		print("[server] Loading server configuration..")
		self.configPath = configPath[0]
		self.loadConfig(configPath[0])
		if not self.error:
			print("[server] Loading up server socketAPI..")
			self.setupSocket()


	def loadConfig(self, configPath):
		try:
			with open(configPath) as f:
				try:
					jsonConfig = json.load(f)
				except:
					print("[Error] (server) Configuration file passed is not valid json.")
					self.error = True
				try:
					self.host = jsonConfig['host']
					self.port = jsonConfig['port']
					self.maxClients = jsonConfig['maxclients']
					self.users = jsonConfig['users']
				except KeyError:
					print("[Error]Invalid Config {0}'".format(configPath))
					self.error = True
		except FileNotFoundError:
			print("[Error] (server) Invalid Config {0}".format(configPath))
			self.error = True


	def saveConfig(self):
		config = {
            "host" : self.host, 
            "port" : self.port, 
            "maxclients" : self.maxClients,
            "users" : self.users
		}
		with open(self.configPath, 'w') as of:
			json.dump(config, of)
    

	def setupSocket(self):
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.bind((self.host, self.port))
		except Exception as e:
			print("[Error - server] Socket Error ",self.port, self.host)
			self.error = True
			print(e)


	def start(self):
		print("[server] Incoming connection : {0}:{1}...".format(self.host, self.port))
		while self.run:
			self.server.listen(1)
			clientSocket, clientAddress = self.server.accept()
			if len(self.activeConnections) == self.maxClients:
				clientSocket.send("FULL".encode('utf-8'))
				clientSocket.close()
				print("[server] FULL ({0}).".format(self.maxClients))
				continue
			clientThread = ClientConnection(self, clientSocket, clientAddress)
			clientThread.start()
		print("[server] Terminating")
		self.server.close()
    

	def login(self, id, objRef):
		for user in self.activeConnections:
			user[1].send("{0} has joined the chatroom.".format(id))
		self.activeConnections.append((id, objRef))
    

	def logOut(self, id):
		for i, ct in enumerate(self.activeConnections):
			if id == ct[0]:
				del self.activeConnections[i]
		for user in self.activeConnections:
			user[1].send("{0} has left".format(id))


	def isLoggedIn(self, uid):
		
		for user in self.activeConnections:
			if user[0] == uid:
				return True
		return False

	def addUser(self, uid, password):
		self.users.append({'userid': uid, 'password': password})
		self.saveConfig()
    

	def sendToAll(self, senderID, message):
		for conn in self.activeConnections:
			conn[1].send("{0}: {1}".format(senderID, message))
		print("[server] {0} (to all): {1}".format(senderID, message))

	def sendToUser(self, senderId, uid, message):
		for conn in self.activeConnections:
			if conn[0] == uid:
				conn[1].send("{0} says to you: {1}".format(senderId, message))
		print("[server] {0} (to {1}): {2}".format(senderId, uid, message))


	def exit(self):
		self.run = False
		return


class Client():
	def __init__(self, server, port):
		self.run = False
		self.server = server
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
	def connect(self):
		try:
			self.socket.connect((self.server, self.port))
			return True
		except:
			print("[Error - client] Server is not running.")
		return False
            
	def listen(self):
		while self.run:
			recvData = self.socket.recv(1024)
			if recvData:
				print(">> {0}".format(recvData.decode().split('\n', 1)[0]))
			else:
				self.stop()

	def send(self, msg):
		msg += '\n'
		try:
			self.socket.sendall('{payload: <{maxlen}}'.format(payload=msg, maxlen=1024).encode('utf-8'))
		except:
			print("[Error - client] Connection to server lost.")
			return False
		return True

	def start(self):
		self.run = True
		listenThread = threading.Thread(target=self.listen)
		listenThread.start()

	def stop(self):
		self.run = False
		self.socket.close()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Chatroom V2", epilog="client mode default")
	parser.add_argument("-s", "--server", help="Runs the application in server mode.", action="store_true")
	parser.add_argument("-c", "--config", nargs=1, help="file path for user login info", action="store")
	args = parser.parse_args()

	if args.server:
		if not args.config:
			print("[Error - server] No config -config, -c.")
			sys.exit(1)
		server = Server(args.config)
		if server.error:
			print("[Error - server] Exiting.")
			sys.exit(1)
		server.start()
	else:
		SERVER = "localhost"
		PORT = 14770
		client = Client(SERVER, PORT)
		if client.connect():
			client.start()
			while True:
				output = input("")
				if output == "logout":
					client.send("logout")
					client.stop()
					break
				else:
					if not client.send(output):
						break
		sys.exit()
