import Pyro4
import os
import threading
import time
import datetime

class Client(threading.Thread):

	def __init__(self, name, path):
		threading.Thread.__init__(self)
		self.thread_stop = False
		self.name = name
		self.path = path
		# connect to the server
		self.centralServer = Pyro4.Proxy("PYRONAME:example.centralServer")
 		self.centralServer.addClientNum()
		#print self.centralServer.getClientNum()
		# send the share files to the server
		fileList = open('%sfiles.txt' % (self.name), 'w')
		files = self.getFiles()
		for item in files:
			fileList.write('%s\n' % (item))
		fileList.close()
		self.centralServer.updateFiles(self.name, files)
		print self.centralServer.welcome()

	def getFiles(self):
		return os.listdir(self.path)

	def closeCon(self):
		# close the connection
		self.centralServer.delClientNum()
		print self.centralServer.getClientNum()
		self.centralServer.delClient(self.name)
		#os.remove('%sfiles.txt' % (self.name))
		self.centralServer._pyroRelease()
		
	def run(self):
		while not self.thread_stop:
			cmd = raw_input("Enter your command: ").strip()
			while cmd != 'shutdown':
				if cmd == 'getFileList':
					# show all the share files
					fullFileList = self.centralServer.getFullFileList()
					print '=' * 30
					print 'Onwer'.ljust(10), 'Files'.ljust(10)
					print '-' * 30
					for oneFile in fullFileList:
						items = oneFile.strip().split()
						print items[0].ljust(10), items[1].ljust(10)
					print '=' * 30
				elif cmd.startswith('search'):
					# search the particular file
					items = cmd.split()
					targetFile = items[1].strip()
					res = self.centralServer.search(targetFile)
					if  res != '-1':
						print 'The file %s is in peer %s' % (targetFile, res)
					else:
						print 'No such a file in this system'
				elif cmd.startswith('download'):
					# download the file
					items = cmd.split()
					serverName = items[1]
					targetFile = items[2]
					#starttime = datetime.datetime.now()
					clientServer = Pyro4.Proxy("PYRONAME:example.%s" % (serverName))
					#print '123'
					#print clientServer.welcome()
					fileContent = clientServer.download(targetFile)
					#print '234'
					newFile = open('%s/%s' % (self.path, targetFile), 'wb')
					newFile.write(fileContent)
					newFile.close()
					clientServer._pyroRelease()
					self.centralServer.updateFile(self.name, targetFile)
					newFile = open('%sfiles.txt' % (self.name), 'a')
					newFile.write('%s\n' % (targetFile))
					newFile.close()
					#endtime = datetime.datetime.now()
					#print str((endtime - starttime).microseconds)
				cmd = raw_input("Enter your command: ").strip()
			if cmd == 'shutdown':
				self.stop()

	def stop(self):
		self.closeCon()
		self.thread_stop = True

class Server(threading.Thread):

	def __init__(self, name, path):
		threading.Thread.__init__(self)
		self.thread_stop = False
		self.name = name
		self.path = path
		daemon = Pyro4.Daemon()
		ns = Pyro4.locateNS()
		uri = daemon.register(self)
		ns.register("example.%s" % (self.name), uri)
		daemon.requestLoop()

	def welcome(self):
		return 'connect to %s' % (self.name)

	def download(self, targetFile):
		theFile = open('%s/%s' % (self.path, targetFile), 'rb')
		fileData = theFile.read()
		theFile.close()
		return fileData

class DoCheck(threading.Thread):

	def __init__(self, name, path, centralServer):
		threading.Thread.__init__(self)
		self.name = name
		self.path = path
		self.centralServer = centralServer
	
	def checkFile(self):
		#print 'hello'
		newFiles = []
		delFiles = []
		fileChanges = False
		fileList = open('%sfiles.txt' % (self.name), 'r')
		recFiles = fileList.readlines()
		files = self.getFiles()
		for eachFile in files:
			#if eachFile == 'abc':
			#	print 'abc'
			if '%s\n' % (eachFile) not in recFiles:
				newFiles.append(eachFile)
				fileChanges = True
		for eachFile in recFiles:
			if eachFile.strip() not in files:
				delFiles.append(eachFile.strip())
				fileChanges = True
		fileList.close()
		if fileChanges:
			if newFiles.__len__() != 0:
				self.centralServer.updateFiles(self.name, newFiles)
				fileList = open('%sfiles.txt' % (self.name), 'a')
				for eachFile in newFiles:
					fileList.write('%s\n' % (eachFile))
				fileList.close()
			if delFiles.__len__() != 0:
				self.centralServer.delFiles(self.name, delFiles)
				fileList = open('%sfiles.txt' % (self.name), 'r')
				recFiles = fileList.readlines()
				theFiles = []
				for oneFile in recFiles:
					if oneFile.strip() not in delFiles:
						theFiles.append(oneFile.strip())
				fileList.close()
				fileList = open('%sfiles.txt' % (self.name), 'w')
				for oneFile in theFiles:
					fileList.write('%s\n' % (oneFile))
				fileList.close()

	def getFiles(self):
		return os.listdir(self.path)

	def run(self):
		while True:
			self.checkFile()
			time.sleep(5.0)

def noSuchPath(path):
	if os.path.isdir(path):
		return False
	else:
		return True

def main():

	# get the name and share directory
	name = raw_input("Enter your name: ").strip()
	path = raw_input("Enter the directory that you will share: ").strip()
	# if no such a directory, input again
	while noSuchPath(path):
		path = raw_input("No such a directory. Enter the directory that you will share: ").strip()
	
	try:
		client = Client(name, path)
		client.start()
		doCheck = DoCheck(name, path, client.centralServer)
		doCheck.start()
		server = Server(name, path)
		server.start()
	except Pyro4.errors.CommunicationError:
		print "The network communication problems."
	except Pyro4.errors.ConnectionClosedError:
		print "The connection was unexpectedly closed."
	except Pyro4.errors.DaemonError:
		print "The daemon encountered a problem."
	except Pyro4.errors.NamingError:
		print "There was a problem related to the name server or object names."

if __name__ == '__main__':
	main()
