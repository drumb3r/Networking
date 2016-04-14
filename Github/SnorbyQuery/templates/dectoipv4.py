#Transformar un formato decimal en IPV4
import ipaddress
conteo = 0

while True:
	decimal = int(raw_input(':'))
	print '%d -------> %s'%(decimal,ipaddress.IPv4Address(decimal))
	conteo += 1
	if decimal ==99:
		break
conteo -= 1				
print 'total de %d ip procesadas'%conteo
		

