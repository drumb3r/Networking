import pyodbc
from time import sleep

DSN = 'odbc-dbname'
USER = 'default'
PASS = 'Harinapan.'
DATABASE = 'Main_Data'
_id = []
_name = []
_dep = []
timeIN,timeOUT,dateIN,dateOUT = '','','',''
n,f_IN,f_OUT = 0,0,0

# Connect Database
try:
	con_string = 'DSN=%s; UID=%s; PWD=%s; DATABASE=%s'%(DSN,USER,PASS,DATABASE)
	conx = pyodbc.connect(con_string)
	cursor = conx.cursor()
	curs = conx.cursor()
	cursor.execute('SELECT * FROM INFORMATION_SCHEMA.TABLES')
	rol = cursor.fetchone()
	database  = rol[0]
	print "Succesfully connect to: %s DB \n"%database
except:
	print "Unable to connect DB, Check Settings"
	
#finding total registered users
cursor.execute('SELECT PER_CODE AS USER_ID FROM HR_PERSONNEL') 
row_len = cursor.fetchall()
print "There are %s registers"%(len(row_len))

#Finding users id, name and department
print "REGISTERED USERS IN DB: "
for row in cursor.execute('SELECT PER_CODE AS ID, PER_NAME, DEPT_NAME AS DEPARTAMENTO FROM HR_PERSONNEL'):
	user_ID = repr(row.ID).strip("u'").strip()
	user_NAME = repr(row.PER_NAME).strip("u'").strip()
	user_DEP = repr(row.DEPARTAMENTO).strip("u'").strip()
	_id.append(user_ID)
	_name.append(user_NAME)
	_dep.append(user_DEP)
for x in range (len(_id)):
	print _id[x], _name[x], _dep[x]	
		
# Encontrando y ordenando	
print "\nSelect which User ID you need to query"
u_id = str(raw_input(":"))
u_name = _name[_id.index(u_id)]
print "SELECTED:",u_id,u_name
date_time = cursor.execute('SELECT DATE_TIME FROM TA_RECORD_INFO WHERE PER_CODE = ? ORDER BY DATE_TIME',u_id).fetchall()
check_table = cursor.execute('SELECT U_DATE FROM TA_SORTED WHERE U_ID = ? ORDER BY U_DATE',u_id).fetchall()
for x in range(0,len(date_time)):
	newR = repr(date_time[x]).split(" ")
	date = newR[0].strip("(u'")
	time = newR[1].strip("',")[0:5]
	if (time > "07:00") and (time < "11:59"):
		timeIN = time
		dateIN = date								
	else:
		timeOUT = time
		dateOUT = date
	print "pase x =",x,date,timeIN,timeOUT			
	if x % 2 == 0:  # por cada dos pasos de x dentengo y verifico los datos
		sleep(0.09)
		if dateIN == dateOUT:  # Si las fechas son iguales, tengo una hora de entrada y una de salida del mismo dia
			f_IN = 1
			f_OUT = 1			
			print "-----%s IN: %s ----- OUT: %s"%(date,timeIN,timeOUT) #INSERTO
			if str(check_table).count(date) == 0:  # verifico si ese dia existe en la DB, de no hacerlo pues lo inserta
				cursor.execute("INSERT INTO TA_SORTED VALUES(?,?,?,?,?)",u_id,u_name,date,timeIN,timeOUT)
			timeIN,timeOUT = '',''
			print "*************************"
		else:  # Si no son iguales las fechas, se averigua de cuando es cada una
			f_IN,f_OUT = 0,0  # Reseteamos todas las variables de interes
			timeIN,timeOUT = "",""  # idem
			if (time > "07:00") and (time < "11:59"):
				f_IN = 1
				timeIN = time
			else:
				f_OUT = 1
				timeOUT = time
			if f_IN == 1 and f_OUT==0:  # si encontramos una hora de entrada pero ninguna de salida
				print "----------Solo marca entrada",date,timeIN,"\n" #INSERTO
				if str(check_table).count(date) == 0:
					cursor.execute("INSERT INTO TA_SORTED VALUES(?,?,?,?,?)",u_id,u_name,date,timeIN,timeOUT)
				timeIN = ''
			elif f_OUT == 1 and f_IN == 0:  # si encontramos una hora de salida pero ninguna de entrada
				print "----------solo marca salida",date,timeOUT,"\n" #INSERTO
				if str(check_table).count(date) == 0:
					cursor.execute("INSERT INTO TA_SORTED VALUES(?,?,?,?,?)",u_id,u_name,date,timeIN,timeOUT)
				timeOUT = ''
	conx.commit()
					
		
	
		
'''
	n += 1			
	if n % 2 != 0:  # por cada dos pases obtengo un resultado (idoneamente un tiempo de entrada y uno de salida)
		if str(check_table).count(date) == 0:
			cursor.execute("INSERT INTO TA_SORTED VALUES(?,?,?,?,?)",u_id,u_name,date,timeIN,timeOUT)
			timeIN = ''
			timeOUT = ''
			conx.commit()				
print "No se inserta en DB",date,timeIN,timeOUT  # si termina el ciclo y queda en un conteo impar, se imprime el ultimo resultado
'''
