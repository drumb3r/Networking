import MySQLdb  # DB Connector
import ipaddress  # Transform Decimal IP to IPv4
from IPy import IP  # Know if the IP is PUBLIC OR PRIVATE
from time import sleep

DBH = '192.168.1.101'
DBU = 'snorby'
DBP = 'mysqlpassword'
DBN = 'snorby'
ip_src,ip_dst,ip_src_v4,ip_dst_v4,block_ip= [],[],[],[],[]
ips={}
ports={}
events=[]
know_ports = [20,21,22,25,80,143,443]

def connect():
	global cursor
	try:
		con_string = [DBH,DBU,DBP,DBN]
		conx = MySQLdb.connect(*con_string) 
		cursor = conx.cursor()
		cursor.execute('SELECT TABLE_SCHEMA FROM INFORMATION_SCHEMA.TABLES')
		cursor.fetchone()
		print "[*]Sucessfully connection to snorby DB \n"
		return conx, cursor
	except Exception, e:
		print "Unable to connect to specific database",e
		exit(0)
					
def know_attackers_ip(event_number=15):
	print '\n[+]fetching querys over',event_number,'number of events'	
	#obtengo conx y cursor de la funcion connect
	conx,cursor = connect()
	cursor.execute('SELECT ip_src,ip_dst,event_id FROM aggregated_events WHERE number_of_events > %s ORDER BY number_of_events DESC',(event_number))
	row = cursor.fetchone()	
	while row is not None:
		ip_src = row[0]
		ip_dst = row[1]
		event_id = row[2]		
		if not '32322' in str(ip_src):  #got an public IPV4 en a event_id, time for port search
			ipsrc = decimal_to_ip(ip_src)
			ips[event_id] = ipsrc
		if not '32322' in str(ip_dst):
			ipdst = decimal_to_ip(ip_dst)
			ips[event_id] = ipdst
		row = cursor.fetchone()
	for enum,event_num in enumerate(ips.keys()):		
		cursor.execute('SELECT * FROM tcphdr WHERE cid = "%s"',[event_num])
		row = cursor.fetchone()
		while row is not None:
			tcp_src,tcp_dst = row[2],row[3]				
			if int(tcp_src) in know_ports:
				print '%s:%s'%(ips[event_num],tcp_src)
			if int(tcp_dst) in know_ports:
				print '%s:%s'%(ips[event_num],tcp_dst)								
			else:
				pass
			row = cursor.fetchone()
			
def decimal_to_ip(ip_dec):
	ipv4 = ipaddress.IPv4Address(ip_dec)
	return str(ipv4)
				
def main():
	sensibility = str(raw_input('Insert Sensibility Search (15):'))
	if len(sensibility) == 0:
		know_attackers_ip()
	else:
		know_attackers_ip(sensibility)
	#print block_ip
	
if __name__ == '__main__':
	main()
	
