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
config.readfp(open(r'snorbyquery.conf'))
DBH = config.get('db-parameters', 'host')
DBU = config.get('db-parameters', 'user')
DBP = config.get('db-parameters', 'password')
DBN = config.get('db-parameters', 'dbname')

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
	cursor.execute('SELECT ip_src,ip_dst,event_id FROM aggregated_events WHERE number_of_events > %s ORDER BY number_of_events DESC',(event_number))
	row = cursor.fetchone()	
	while row is not None:  # hasta que finalice el cursor.fetchone de toda la consulta SQL
		ip_src = row[0]
		ip_dst = row[1]
		event_id = row[2]		
		if not '32322' in str(ip_src):  #32322 eq to 192.168, means that IP is not public 
			ipsrc = decimal_to_ip(ip_src)  # transformo ip de decimal a IPV4
			ips[event_id] = ipsrc  # agrego en un diccionario con formato 'event_id: ip'
		if not '32322' in str(ip_dst):
			ipdst = decimal_to_ip(ip_dst)  # IDEM
			ips[event_id] = ipdst  # IDEM
		row = cursor.fetchone()  # al terminar con la fila actual, actualizo a la siguiente. cuando no existan mas termina el while
	for enum,event_num in enumerate(ips.keys()):		
		cursor.execute('SELECT * FROM tcphdr WHERE cid = "%s"',[event_num])  # ahora busco con el event_id el puerto de esa direccion IP
		row = cursor.fetchone()		
		while row is not None:
			tcp_src,tcp_dst = row[2],row[3]				
			if int(tcp_src) in know_ports:  # puerto de origen, esta incluido en la lista de puertos conocidos?
				ip = ips[event_num]  # de ser asi, imprimo la IP que se asocia en ese evento
				port = int(tcp_src)  # imprimo el puerto (que se esta en la corrida actual del while)
				print enum,'[+] %s:%s'%(ip,port)  # imprimo serial
				blocked_ips[ip] = port  # agrega en un diccionario 'ip:puerto' que se imprimira en la funcion main
			if int(tcp_dst) in know_ports:  # puerto de destino, esta incluido en la lista de puertos conocidos?
				ip = ips[event_num]  # IDEM
				port = int(tcp_dst)  # IDEM
				print enum,'[+] %s:%s'%(ip,port)  # IDEM
				blocked_ips[ip] = port  # IDEM							
			else:  # si el puerto no esta en la lista de puertos conocidos, pasa al siguiente
				pass
			row = cursor.fetchone()
	cursor.close()
	conx.close()
			
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
		file.write('%s:%s'%(ip,port))
		file.write('\n')
	file.close()
	
	
if __name__ == '__main__':
	main()
	
