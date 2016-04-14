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
		print "Sucessfully connection to snorby DB"
		return conx, cursor
	except Exception, e:
		print "Unable to connect to specific database",e
		exit(0)
					
def know_attackers_ip():
	#obtengo conx y cursor de la funcion connect
	conx,cursor = connect()
	cursor.execute('SELECT ip_src,ip_dst,event_id FROM aggregated_events WHERE number_of_events > 15 ORDER BY number_of_events DESC')
	row = cursor.fetchone()	
	while row is not None:
		ip_src = row[0]
		ip_dst = row[1]
		event_id = row[2]		
		if not '32322' in str(ip_src):  #got an public IPV4 en a event_id, time for port search
			ipsrc = decimal_to_ip(ip_src)
			ips[ipsrc] = event_id
		if not '32322' in str(ip_dst):
			ipdst = decimal_to_ip(ip_dst)
			ips[ipdst] = event_id
		row = cursor.fetchone()
	for enum,event_num in enumerate(ips.values()):
		print enum,event_num
		cursor.execute('SELECT * FROM tcphdr WHERE cid = "%s"',[event_num])
		row = cursor.fetchone()
		while row is not None:
			tcp_src,tcp_dst = row[2],row[3]				
			if int(tcp_src) in know_ports or int(tcp_dst) in know_ports:
				print tcp_src,'----->',tcp_dst,' | ',event_num, '\n'
			else:
				pass
			row = cursor.fetchone()
			
def decimal_to_ip(ip_dec):
	ipv4 = ipaddress.IPv4Address(ip_dec)
	return str(ipv4)
				
def main():
	know_attackers_ip()
	print block_ip
	
if __name__ == '__main__':
	main()
	
