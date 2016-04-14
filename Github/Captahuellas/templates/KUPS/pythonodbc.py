import pyodbc
from time import sleep

_id = []  # USERS ID
_name = []  # USERS NAME
_dep = []  # USERS DEPARTMENT
db_IN = ''  # USERS IN  
db_OUT = ''  # USERS OUT
db_date = ''
prev_date,prev_time = '',''
next_date,next_time = '',''

f_IN,f_OUT = 0,0
dita = 0


dict = {}
DSN = 'odbc-dbname'
USER = 'default'
PASS = 'J18688973.'
DATABASE = 'Main_Data'

# Connect Database
try:
	con_string = 'DSN=%s; UID=%s; PWD=%s; DATABASE=%s'%(DSN,USER,PASS,DATABASE)
	conx = pyodbc.connect(con_string)
	cursor = conx.cursor()
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
	
#Finding Time Access Logins
for row in cursor.execute('SELECT PER_CODE AS ID, DATE_TIME AS LOGIN FROM TA_RECORD_INFO'):	
	user_ID = repr(row.ID).strip("u'").strip()
	user_Login = repr(row.LOGIN).strip("u'").strip()				
	if dict.has_key(user_ID):
		if user_Login not in dict[user_ID]:
			dict[user_ID].append(user_Login)
	else:
		dict[user_ID] = []
		dict[user_ID].append(user_Login)
	
# Finding IN_TIME, OUT_TIME and DATE of each user
print "\nSelect which User ID you need to query"
n_id = str(raw_input(":"))
index = _id.index(n_id)  # select where is located in _id the user that we entry. 
for x in range(0,len(dict[n_id])):	
	date = dict[n_id][x].split(" ")[0]
	time = dict[n_id][x].split(" ")[1][0:5]	
	if date == db_date:
		if (time > "12:00") and (time < "23:00"):
			db_OUT = time
			f_OUT = 1  # En la misma fecha pero en el segundo recorrido hay salida
	else:				
		if f_OUT == 1 and (db_OUT != time):
			prev_date,prev_time = db_date,db_OUT
			next_date,next_time = date,time
			#print db_date, db_OUT 
			#print date,time						
			reply = 2
		elif f_IN == 1 and db_IN != time:
			prev_date,prev_time = db_date,db_IN
			next_date,next_time = date,time
			reply = 2			 											
		if (time > "07:00") and (time < "11:59"):		
			db_IN = time
			f_IN = 1							
		if (time > "12:00") and (time < "23:00"):		
			db_OUT = time	# salida solamente
			f_IN = 0
			f_OUT = 1
		db_date = date
	if x == 0:
		continue					
		
#       //////////////////////////////////////////////////////// 					
	if (x % 2 != 0):  # por cada dos ciclos obtengo una conclusion		
		if (f_IN == 1) and (f_OUT == 1):  # Existe registro de entrada y salida en la misma fecha?
			print date, db_IN, db_OUT
			db_IN = ''
			db_OUT = ''
			f_IN = 0
			f_OUT = 0					
		elif f_IN == 1 and f_OUT == 0 and reply != 2:  # Existe solamente un registro de entrada con fechas distintas?
			print "After mod 2", date,time,repr(f_IN), repr(f_OUT) 
			f_IN = 0
		elif f_IN == 0 and f_OUT == 1 and reply != 2:  # Existe solamente un registro de salida con fechas distintas?
			print date,time 
			f_OUT = 0
		if reply == 2:
			print prev_date,prev_time
			print next_date,next_time
			reply = 0
