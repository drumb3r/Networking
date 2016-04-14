# DNSRR Iteration: http://stackoverflow.com/questions/12501780/dnsrr-iteration

from scapy.all import *
import dpkt
import socket
from IPy import IP as IPT

ip_ttl = {}
newip = {}
THRESH = 20

def iptype(ip):
	if IPT(ip).iptype() == 'PRIVATE' or IPT(ip).iptype() == 'RESERVED' :
		return 
	else:
		return ip
			

def findIP(pcap):	
	try:
		#print pcap.summary()		
		if pcap.haslayer(IP):
			ip_src = pcap.getlayer(IP).src  # Obtengo IP Origen
			ip_dst = pcap.getlayer(IP).dst  # Obtengo IP Destino
			ttl = str(pcap.ttl)  # Obtengo TTL						
			typeIP = iptype(ip_dst)  # Obtengo tipo de IPV4	de la funcion						
			if typeIP == None:  # la ip recibida es privada, sin embargo...
				if pcap.haslayer(UDP):  # Se buscan las solicitudes DNS(1/2)
					if pcap.getlayer(UDP).sport == 53 or pcap.getlayer(UDP).dport == 53:  # Mediante este filtro(2/2)
						#print pcap.show()
						dns = pcap['DNS']
						print "[*][*]Query DNS detected to: ",pcap.getlayer(DNSRR).rrname,"| Server",ip_src						
						for index,cant in enumerate(range(dns.ancount)):  # si existe mas de una direccion ip para resolver
							dnsrr = dns.an[cant]							
							print index," - ",dnsrr.rdata							
						print "\n \n"
						#exit(0)
			else:  # la IP obtenida es publica
				if pcap.haslayer(TCP):  # aparte, de esa IP publica se verifica si hay una conexion TCP					
					tcp_sport = pcap.getlayer(TCP).sport  # se obtiene desde que puerto se establece
					tcp_dport = pcap.getlayer(TCP).dport  # a que puerto de destino se establece					
					if not ip_ttl.has_key(ip_dst): # Si no existe la IP de la cual se ha establecido el socket TCP se agrega
						pkt = sr1(IP(dst=ip_dst)/ICMP(), retry=0, timeout=1, verbose=0)  # se envia un PING para verificar ttl
						ip_ttl[ip_dst] = pkt.ttl  # se obtienen ttl						
						print "[+]SOCKET CONNECTION: %s with TTL: %s **** SPORT: %s - DPORT: %s"%(typeIP,ttl,tcp_sport,tcp_dport)
						if ttl and ip_ttl:
							difference = abs(int(ttl)-int(ip_ttl[ip_dst]))  # Diferencia entre ambos TTL
							print "IP sniffed TTL:",ttl
							print "After send PING with Scapy TTL:",ip_ttl[ip_dst]						
							print "Difference between booth:",repr(difference)+"\n"
							if difference > THRESH:
								print "[!][*]Spoofing connection from %s ? \n \n"%ip_dst	#'''TODO resolve IP ADDR'''					
				else:  # Si no se ha establecido una conexion socket TCP con algun puerto de la IP publica
					if not newip.has_key(ip_dst):
						newip[ip_dst] = 1  # Se agrega a un diccionario para que no se repita en la pantalla (filtrarla)
						print "[!]PUBLIC IP DETECTED: %s with TTL: %s without TCP Layer... (UDP?)"%(typeIP,ttl)
					else:
						pass						
	except Exception, e:
		#print "Error:",e
		pass
		

def main():
	sniff(prn=findIP, store=0)
	
	
if __name__=="__main__":
	main()
