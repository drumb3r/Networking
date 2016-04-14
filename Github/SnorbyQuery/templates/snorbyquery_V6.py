'''
<top> Usando MySQL para conectar a la DB del frontend Snorby. </top>

este script conecta a la base de datos snorby y busca eventos mayores a 15 (por defecto). Una vez encontrados los eventos,
solo de esos se obtienen los que sean desde IP publica (NAT, red WAN) y los puertos sean conocidos. Se imprimen en un archivo .txt 
el cual es leido por un script en powershell desde windows server y agrega dicha direccion ip:puerto a una regla en Windows Firewall
si se cambia la ip muchas veces entonces se detiene el servicio que corre por ese puerto y genera una alarma en el servidor.  

'''
import MySQLdb  # DB Connector
import ipaddress  # Transform Decimal IP to IPv4
import ConfigParser
from IPy import IP  # Know if the IP is PUBLIC OR PRIVATE
from time import sleep  # just for inspect for and while loops

#db parameters from configuration file
config = ConfigParser.ConfigParser()
try:
	config.readfp(open(r'snorbyquery.conf'))
	#DB PARAMETERS
	DBH = config.get('db-parameters', 'host')
	DBU = config.get('db-parameters', 'user')
	DBP = config.get('db-parameters', 'password')
	DBN = config.get('db-parameters', 'dbname')
	#FILE PARAMETERS
	show_ports = config.get('print-options', 'ShowPorts')
except Exception,e:
	print e
	exit(0)

events,ip_src,ip_dst,ip_src_v4,ip_dst_v4= [],[],[],[],[]
ports,ips,blocked_ips={},{},{}
know_ports = [20,21,22,25,80,143,443]

def connect():  # probar conexion SQL y devolver cursor y conexion
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
					
def know_attackers_ip(event_number=15):  # listar mayor numero de eventos, obtener ip publica y puerto de conexion
	print '\n[+]fetching querys over',event_number,'number of events'		
	conx,cursor = connect()  #obtengo conx y cursor de la funcion connect
	cursor.execute('SELECT ip_src,ip_dst,event_id,number_of_events FROM aggregated_events WHERE number_of_events > %s ORDER BY number_of_events DESC',(event_number))
	results = cursor.fetchall()
	for row in results:
		ip_src = row[0]
		ip_dst = row[1]
		actual_event_id = row[2]
		number_of_events = row[3]
		if not '32322' in str(ip_src):
			ipsrc = decimal_to_ip(ip_src)  # append ip to block			
			port = know_attackers_port(ipsrc,actual_event_id)  # IPV4 port
			if port != None:
				blocked_ips[ipsrc] = port  # append ip:port format
		if not '32322' in str(ip_dst):
			ipdst = decimal_to_ip(ip_dst)  # ip in IPV4 format			
			port = know_attackers_port(ipdst,actual_event_id)  # IPV4 port
			if port != None:
				blocked_ips[ipdst] = port  # append ip:port format
			
def know_attackers_port(ip,event_num):	
	cursor.execute('SELECT * FROM tcphdr WHERE cid = "%s"',[event_num])
	results = cursor.fetchall()
	for row in results:
		tcp_sport = row[2]
		tcp_dport = row[3]
		if tcp_sport in know_ports:		
			return tcp_sport
		if tcp_dport in know_ports:			
			return tcp_dport
		return None
	
def decimal_to_ip(ip_dec):  # convertir la ip de formato decimal a IPV4
	ipv4 = ipaddress.IPv4Address(ip_dec)
	return str(ipv4)
				
def main():	
	sensibility = str(raw_input('Insert Sensibility Search (15):'))  # buscar numero de eventos > 'sensibility'
	if len(sensibility) == 0:  
		know_attackers_ip()
	else:
		know_attackers_ip(sensibility) 
	# print in .txt for powershell script firewall rule append
	file = open('iplist.txt','w')	
	for ip,port in blocked_ips.items():
		if show_ports == 'True':
			file.write('%s:%s'%(ip,port))
			file.write('\n')
		else:
			file.write(ip)
			file.write('\n')
	file.close()
	print '[*]File "iplist.txt" has been generated' 
		
if __name__ == '__main__':
	main()
	
