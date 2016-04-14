import pyodbc
from time import sleep

DSN = 'odbc-dbname'
USER = 'default'
PASS = 'Harinapan.'
DATABASE = 'Main_Data'
_id = []
_name = []
_dep = []
timeIN,timeOUT = '',''
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
date_time = cursor.execute('SELECT DATE_TIME FROM TA_RECORD_INFO WHERE PER_CODE = ?',u_id).fetchall()
check_table = cursor.execute('SELECT U_DATE FROM TA_SORTED WHERE U_ID = ? ORDER BY U_DATE',u_id).fetchall()
for x in range(0,len(date_time)):
	newR = repr(date_time[x]).split(" ")
	date = newR[0].strip("(u'")
	time = newR[1].strip("',")[0:5]
	if (time > "07:00") and (time < "11:59"):
		timeIN = time				
	else:
		timeOUT = time
	n += 1			
	if n % 2 != 0:  # por cada dos pases obtengo un resultado (idoneamente un tiempo de entrada y uno de salida)
		if str(check_table).count(date) == 0:
			cursor.execute("INSERT INTO TA_SORTED VALUES(?,?,?,?,?)",u_id,u_name,date,timeIN,timeOUT)
			timeIN = ''
			timeOUT = ''
			conx.commit()
			'''				
# si el cilo queda en un paso impar, se imprime (recordando que el cheque de IN y OUT se hace por cada 2 ciclos)
timeIN = ''
timeOUT = ''
if (time > "07:00") and (time < "11:59"):
	timeIN = time				
else:
	timeOUT = time
cursor.execute("INSERT INTO TA_SORTED VALUES(?,?,?,?,?)",u_id,u_name,date,timeIN,timeOUT)
print "No se inserta en DB",date,timeIN,timeOUT  # si termina el ciclo y queda en un conteo impar, se imprime el ultimo resultado
conx.commit()
'''
