#SSH Client
import paramiko
import subprocess

def ssh(ip,port,user,passwd,command,home_user):	 
	client = paramiko.SSHClient()
	client.load_host_keys('/home/%s/.ssh/known_hosts'%(home_user))
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(ip , port=port , username=user , password=passwd)
	ssh_session = client.get_transport().open_session()
	if ssh_session.active:
		ssh_session.exec_command(command)
		print "[*]RESPONSE CHAIN: \n",ssh_session.recv(1024)
	return

def main():
	home_user = subprocess.Popen('echo $USER', stdout=subprocess.PIPE, shell=True)
	user = home_user.communicate()[0].strip()
	ssh('127.0.0.1',3322,'jonn3y','j18688973','cat /etc/passwd',user)
	
if __name__=="__main__":
	main()
