import socket
import sys
import argparse
import threading
import os
import time

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 47743
SERVER_ADDR = (SERVER_HOST, SERVER_PORT)

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
connection.bind(SERVER_ADDR)
connection.listen(10)

respBod = ''
respHeads = ''

if len(sys.argv) > 1:
	if sys.argv[1] == '--root':
		os.chdir(sys.argv[2])
	else:
		os.chdir("./www")
else:
	os.chdir("./www")

def genHeads(self, code, respBod, conType):
	"""this method actually generates the entire formatted HTTP response and sends it to the client"""
	respHeads = '' 
	if code == 200:
		print("file found")
		respHeads = 'HTTP/1.1 200 OK\n' 
	elif code == 400:
		print("bad request error")
		respBod = b"<html><body><p>Error 400: Bad request</p></body></html>" 
		respHeads = 'HTTP/1.1 400 Bad Request\n'
	elif code == 403:
		print("forbidden request error")
		respBod = b"<html><body><p>Error 403: Forbidden</p></body></html>" 
		respHeads = 'HTTP/1.1 403 Forbidden\n'
	elif code == 404:
		print("file not found error")
		respBod = b"<html><body><p>Error 404: File not found</p></body></html>" 
		respHeads = 'HTTP/1.1 404 Not Found\n' 

	current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	respHeads += 'Date: ' + current_date +'\n'
	respHeads += 'Server: web_server\n'
	respHeads += 'Connection: close\n'
	respHeads += "Content type: " + conType + "\n\n"

	print(respHeads)
	fullResp = respHeads.encode() + respBod
	self.client.send(fullResp)
	return

def parseRequest(written, self, client, address):
	"""parses the decoded request"""
	respBod = ''
	conType = ''
	lineList = written.split("\n")			#splitting the request by newline chars
	commandList = lineList[0].split(" ")	#splitting the commands by space keys
	if commandList[0] != 'GET':				#checking that it is a GET request, send 400 if not
		genHeads(self, 400, respBod, conType)
		return

	fullpath = commandList[1][1:]			#taking the first / off the path string and ignoring url arguments
	fullpath = fullpath.split('?')[0]			

	print("the request is: {}".format(commandList[0]))

	if fullpath == '/' or fullpath == '' or os.path.isdir('./' + fullpath) == True:
		fullpath = 'index.html'				#setting index as the default if the request asks for a directory
	elif fullpath.find('.') == 1:			#finding and setting the content type
		conType = fullpath.split('.')
		conType = conType[1]
		if conType == "png":
			conType = "image/png"
		elif conType == "html":
			conType = "text/html"
		elif conType == "txt":
			conType = "text/html"
	try:									#try to open the file path
		f = open(fullpath,'rb')
		respBod = f.read()					#reading the file and saving it as respBod
		f.close()
		print("got the file")

		genHeads(self, 200, respBod, conType)		#if it all works give 200
	except FileNotFoundError:
		genHeads(self, 404, respBod, conType)
	except PermissionError:
		genHeads(self, 403, respBod, conType)


class HandlerThread(threading.Thread):
	"""Handles threading"""
	def __init__(self, client, address):
		"""constructs the thread for each client that tries to connect"""
		threading.Thread.__init__(self)
		self.client = client
		self.address = address

	def run(self):
		"""this method runs the code and handles getting the data from the client"""
		print('executing thread for client {}'.format(address))
		data = self.client.recv(4096)
		
		if data.endswith("\r\n\r\n".encode()): #if all the data was sent at once, IE through a browser
			data = data
		else:									#else take in the data line by line
			temp = ' '
			while True:
				temp = self.client.recv(4096)
				data += temp
				if temp == b"\r\n":				#break when you get an empty line
					break

		written = data.decode()
		print('received \r{} of length {}'.format(written, len(data)))		#print out the request in full

		parseRequest(written, self, client, address)	#get to parsing an processing

		self.client.close()
		sys.exit()

while True:
	"""infinite loop keeping the program listening for new connections"""
	client, address = connection.accept()
	th = HandlerThread(client, address)
	th.start()

def sigint(sig, dummy):
	self.shutdown()
	sys.exit(1)

signal.signal(signal.SIGINT, graceful_shutdown)