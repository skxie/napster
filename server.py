import Pyro4
import os

class CentralServer:

	def __init__(self):
		self.num = 0
		fileList = open('file_list.txt', 'w')
		fileList.close()

	def updateFiles(self, clientName, files):
		# add new share files in the list
		fileList = open('file_list.txt', 'a')
		for item in files:
			fileList.write(clientName + ' ' + item + '\n')
		fileList.close()

	def updateFile(self, clientName, theFile):
		# add one new share file in the list
		fileList = open('file_list.txt', 'a')
		fileList.write('%s %s\n' % (clientName, theFile))
		fileList.close()

	def search(self, targetFile):
		# search whether a file in this system
		fileList = open('file_list.txt', 'r')
		files = fileList.readlines()
		for eachfile in files:
			item = eachfile.split()
			#print '{0}___{1}'.format(item[0],item[1])
			#print targetFile
			if targetFile == item[1].strip():
				return item[0]
		return '-1'
	
	def delFiles(self, clientName, files):
		fileList = open('file_list.txt', 'r')
		recFiles = fileList.readlines()
		tempFile = open('temp_file.txt', 'w')
		
		for eachFile in recFiles:
			#print '{0}___{1}'.format(eachFile[0],eachFile[1])
			rec = eachFile.split()
			if not (rec[0] == clientName and (rec[1].strip() in files)):
				tempFile.write(eachFile)
		fileList.close()
		tempFile.close()
		fileList = open('file_list.txt', 'w')
		tempFile = open('temp_file.txt', 'r')
		theRec = tempFile.readlines()
		fileList.writelines(theRec)
		fileList.close()
		tempFile.close()
		os.remove('temp_file.txt')

	def delClient(self, clientName):
		# Once one peer is closed, delete the share files from it
		fileList = open('file_list.txt', 'r')
		files = fileList.readlines()
		tempFile = open('temp_file.txt', 'w')
		itemNumber = 0
		for item in files:
			if (item.startswith(clientName) == 0):
				tempFile.write(item)
				itemNumber += 1
		fileList.close()
		tempFile.close()
		if itemNumber != 0:
			fileList = open('file_list.txt', 'w')
			tempFile = open('temp_file.txt', 'r')
			files = tempFile.readlines()
			fileList.writelines(files)
			fileList.close()
			tempFile.close()
		else:
			os.remove('file_list.txt')
		os.remove('temp_file.txt')

	def getFullFileList(self):
		# return all the share files
		fileListFile = open('file_list.txt', 'r')
		fileList = fileListFile.readlines()
		fileListFile.close()
		return fileList

	def welcome(self):
		#return '''
		#Hi, this a p2p system which provides the following functions:
		#1. getFullFileList. get the names of full shared files.
		#2. search. search the specific file to check whether it is shared in this system.
		#3. downlad. download a particular file from a specific peer.
		#'''
		return '''
		Hi, this a p2p system which provides the following functions:
		1. search. search the specific file to check whether it is shared in this system.
		2. downlad. download a particular file from a specific peer.
		'''
	def getClientNum(self):
		return self.num

	def addClientNum(self):
		self.num += 1
		return self.num

	def delClientNum(self):
		self.num -= 1
		return self.num


def main():

	centralServer = CentralServer()
	try:
		daemon = Pyro4.Daemon()
		ns = Pyro4.locateNS()
		uri = daemon.register(centralServer)
		ns.register("example.centralServer", uri)
		print "Ready."
		daemon.requestLoop()
		#cmd = raw_input("If you want to shutdown the server please input 'shutdown'").strip();
		#while (cmd != 'shutdown'):
		#	cmd = raw_input("If you want to shutdown the server please input 'shutdown'").strip();

	except Pyro4.errors.CommunicationError:
		print 'Network communication errors.'
	except Pyro4.errors.ConnectionClosedError:
		print 'The connection was unexpectedly closed.'
	except Pyro4.errors.DaemonError:
		print 'The daemon eoncountered a problem.'
	except Pyro4.errors.NamingError:
		print 'There was a problem related to the name server or object names.'

if __name__ == '__main__':
	main()

