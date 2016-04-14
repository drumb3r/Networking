''' 
PROGRAMACION ZKE Fingerprint THERMOEQUIPOS C.A.

En este Script se necesita mejorar la comunicacion TCP, ya que despues del Handshake TCP (en plena pila PSH,ACK) envia un ACK 
haciendo el rebote del paquete por parte del host. Recomiendo hacer el envio del paquete mediante Scapy descartando socket 

NOTA: El Script funciona con la modificacion de las "iptables"(evitando que el computador envie el RST) debe existir la regla

AGREGAR REGLA: iptables -A OUTPUT -p tcp --tcp-flags RST RST -s 192.168.1.20 -j DROP
BACKUP IPTABLES: iptables-save -c > /root/iptables.rules.backup
RESTORE IPTABLES: iptables-restore -c /root/iptables.rules.backup
'''
from socket import *
import time
import logging


def take_time():
	# ano :         mes           :   dia   :  hora   :  minutos:  segundos:  diasemana
	# 2015:01,02,03 (En, Feb, Mar),   06    :   00H   :    00M  :     00S  :   01,02,03 (Lun, Mar, Mier)
	global ano
	global mes
	global diames
	global hora
	global minutos
	global segundos	
	ano       =    time.strftime("%Y")
	mes       =    time.strftime("%m")
	diames    =    time.strftime("%d")
	hora      =    time.strftime("%H")
	minutos   =    time.strftime("%M")
	segundos  =    time.strftime("%S")
	diasemana =    time.strftime("%w")
	# Splitting Year 2015 - 2016 - 2017....
	hexano = hex(int(time.strftime("%Y")))
	year_1 = hexano[1:3]  # 0x07
	year_2 = "x"+hexano[3:]  # xe0	
	_chain = "\x55\xaa\x01\xb3\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\xbb\x01\x55\xaa\x07\xe0"+ \
	str(unichr(int(mes)))+str(unichr(int(diames)))+str(unichr(int(hora)))+str(unichr(int(minutos)))+ \
	str(unichr(int(segundos)))+str(unichr(int(diasemana)))+"\x00\x00"				
	return _chain	
	
	
def connScan(tgtHost, tgtPort, chain):
	try:
		connSkt = socket(AF_INET, SOCK_STREAM)
		connSkt.connect((tgtHost, tgtPort))
		connSkt.settimeout(10)
		connSkt.send('\x55\xaa\x01\x80\x01\x00\x00\x00\x00\x00\xff\xff\x00\x00\x7f\x03')         # SEND 16B		
		results = connSkt.recv(10)  													     # RECEIVE 10B		
		connSkt.send('\x55\xaa\x01\x81\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x7f\x03')         # SEND 16B		
		results = connSkt.recv(10)  													     # RECEIVE 10B		
		print "Now Programming ZKS..."
		connSkt.send(chain)  															         # SEND 28B
		results = connSkt.recv(10) 													         # RECEIVE 10B		
		connSkt.send('\x55\xaa\x01\x81\x01\x00\x00\x00\x00\x00\xff\xff\x00\x00\x80\x03')         # SEND 16B		
		results = connSkt.recv(10) 													         # RECEIVE FINAL 10B
		if results:
			print "[+]ZKS Has been programmed",repr(results)
			connSkt.close()
			return True		
	except:
		print '[-]%d port CLOSED, Check Connection (Host Alive?)'% tgtPort
		return False
		
def main():
	tgtHost= "192.168.1.120"
	tgtPort=5005
	logging.basicConfig(filename='/home/jonn3y/Fingerprint/ZKS.log',level=logging.DEBUG)
	chain = take_time()
	programZKE = connScan(tgtHost, tgtPort, chain)
	if programZKE:
		logging.info('%s:%s:%s[%s:%s:%s]: [+]ZKS has been programmed'%(diames,mes,ano,hora,minutos,segundos)+'\n')	
	else:
		logging.warning('%s:%s:%s[%s:%s:%s]: [-]ZKS has not been programmed'%(diames,mes,ano,hora,minutos,segundos))
		logging.debug('%s:%s:%s[%s:%s:%s]: [-]%d port CLOSED, Check Connection'%(diames,mes,ano,hora,minutos,segundos,tgtPort)+'\n')
		
			
if __name__ == '__main__':
	main()


	
