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
events=[]

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
		if not '32322' in str(ip_src):
			print 'I=%s , E=%s'%(ip_src,event_id)			
			events.append(event_id)
		if not '32322' in str(ip_dst):
			print 'I=%s , E=%s'%(ip_dst,event_id)
			events.append(event_id)
		row = cursor.fetchone() # the while continue line
	for event_number in events:
		find_port(event_number)
						
def find_port(event_id):
	print event_id
	cursor.execute("SELECT * FROM tcphdr WHERE cid LIKE '%s'",[event_id])
	row = cursor.fetchone()	
	while row is not None:
		tcp_sport = row[2]
		tcp_dport = row[3]
		print tcp_sport,'------->',tcp_dport
		row = cursor.fetchone()
	
def main():
	know_attackers_ip()
	print block_ip
	
if __name__ == '__main__':
	main()
	
