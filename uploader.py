#!/usr/bin/env python
import glob, os, sys

from ftplib import FTP
from slugify import slugify

supported_formats = ("mkv", "avi", "mp3")
working_directory = None


def logger(message):
	print message;

class FtpUploadTracker:
    sizeWritten = 0
    totalSize = 0
    lastShownPercent = 0
    firstTime = True
    
    def __init__(self, totalSize):
        self.totalSize = totalSize
        print "------- UPLOAD STARTED -------\n FILE SIZE: ", totalSize >> 20 , " mb"
		
    def handle(self, block):
        
        self.sizeWritten += 1024
        percentComplete = round((float(self.sizeWritten) / float(self.totalSize)) * 100)
        
	if (self.lastShownPercent != percentComplete):
		self.lastShownPercent = percentComplete
		#print(str(percentComplete) + " percent complete")
		sys.stdout.write("\r UPLOADING PROGRESS: " + str(percentComplete) + "%")
		sys.stdout.flush()
	
def loadIndex(folder):
 	""" Load index in specific folder - index.upload """
	result = [];

	global index_file
	index_file = os.path.join(folder, "index.upload")
	with open(index_file, "a+") as f:
   		result = f.read().splitlines()

	return result;

def writeFileToIndex(file):
	''' Write file to index '''
	with open(index_file, "a+") as f:
		 f.write(file + "\n")

def uploadFile(file):
	
	logger("Connecting to client....");
	
	# Open FTP connection
	ftp = FTP('ftp.streamcloud.eu')
	ftp.login('Pooky5','')
	
	openFile = open(file, 'rb')
	
	uploadTracker = FtpUploadTracker(int(os.path.getsize(file)))
	
		
	fileName, fileExtension = os.path.splitext(os.path.basename(file))

	logger(" FILE NAME: " + fileName + fileExtension)

	ftp.storbinary('STOR ' + slugify(fileName) + fileExtension, openFile, 1024, uploadTracker.handle)
	
	logger("\n-------- UPLOAD CLOSED --------")
	
	ftp.quit()
	openFile.close()
	
def exit(message):
    sys.exit("!!! EXIT !!! \n Message: '" + message + "'")

def main():
	""" Main function for run this program """
	#print uploadedFiles

	''' For each file in folder '''
	for root, subdirs, files in os.walk(working_directory):
		
		filesToUpload = [ fi for fi in files if fi.endswith(supported_formats) ]
		if(len(filesToUpload) > 0):
			uploadedFiles = loadIndex(root)
	    		for file in filesToUpload:
        			if file not in uploadedFiles:
            				print "# >>> Found new file - " , file
            				uploadFile(os.path.join(root,file))
           				writeFileToIndex(file)

	print "DONE";


""" Check arguments and process working directory """
if(len(sys.argv) > 1):

    working_directory = sys.argv[1]
    if(not os.path.isdir(working_directory)):
        exit("Folder is not valid...")
        
else:
    working_directory = os.getcwd()

main()
