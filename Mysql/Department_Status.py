import mysql.connector
import json

mydb = mysql.connector.connect(
    host="localhost",
    user="juefeic2",
    password="0202141208",
    database="juefeic2_educationtoday"
)

mycursor = mydb.cursor()

# sql = "INSERT INTO Faculty_University_Status (University_ID, University_Name, Status) VALUES (%s, %s, %s)"

# f = open('US_Universities.txt', 'r')
# a = 1
# for i in f.readlines():
#     i = i[:-1]
#     print(i)
#     val = (a, i, "None")
#     mycursor.execute(sql, val)
#     a += 1

# mydb.commit()

# print(mycursor.rowcount, "record inserted.")

# mycursor.execute('select * from Department')
# myresult = mycursor.fetchall()

# for i in myresult:
#     sql = "INSERT INTO Faculty_Status (University_ID, Department_Name, Status) VALUES (%s, %s, %s)"
#     val = (i[0][:i[0].find('_')], i[1], 'None')
#     mycursor.execute(sql, val)

# mydb.commit()

# mycursor.execute('select University_Name, Department_Name from Department natural join Department_History natural join University where University_ID < 101')
# res = {}
# r = mycursor.fetchall()
# for i in r:
#     if i[0] not in res:
#         res[i[0]] = []
#     res[i[0]].append(i[1])
# print(len(res))

# f = open('departments_for_top_100_universities.json', 'w')
# json.dump(res, f, indent = 4)

# mycursor.execute('select University_Name, Department_Name from Department natural join Department_History natural join University where University_ID < 101')
# res = {}
# r = mycursor.fetchall()
# for i in r:
#     if i[0] not in res:
#         res[i[0]] = {}
#     mycursor.execute('select University_ID from University where University_Name = "' + i[0] + '"')
#     university_id = mycursor.fetchone()[0]
#     mycursor.execute('select Task_ID from Faculty_History where University_ID = %s and Department_Name = %s', (university_id, i[1]))
#     task_id = mycursor.fetchone()
#     # print(task_id)
#     if not task_id:
#         continue
#     task_id = task_id[0]
#     mycursor.execute('select Name, Position, Research, Email, Phone from Faculty where Task_ID = "' + task_id + '"')
#     l = []
#     info = mycursor.fetchall()
#     for j in info:
#         m = {'Name': j[0], 'Position': j[1], 'Research': j[2], 'Email': j[3], 'Phone': j[4]}
#         l.append(m)
#     res[i[0]][i[1]] = l
#     print(task_id)
# print(len(res))

# f = open('faculty_for_top_100_universities.json', 'w')
# json.dump(res, f, indent = 4)


# CREATE TABLE `Faculty_Tasks` (
#   `University_ID` int(11) DEFAULT NULL,
#   `Department_Name` varchar(200) DEFAULT NULL,
#   `Priority` int(11) NOT NULL
# ); 
mycursor.execute('select University_ID, Department_Name, Status from Faculty_Status order by University_ID asc;')
r = mycursor.fetchall()
n = 0
t = 2 ** 31 - 1
for i in r:
    try:
        if i[2] == 'Finished':
            # mycursor.execute('update Faculty_Status set Priority = {} where University_ID = "{}" and Department_Name = "{}"'.format(str(t), i[0], i[1]))
            mycursor.execute('insert into Faculty_Tasks (University_ID, Department_Name, Priority) values ("{}", "{}", {})'.format(i[0], i[1], str(t)))
        else:
            # mycursor.execute('update Faculty_Status set Priority = {} where University_ID = "{}" and Department_Name = "{}"'.format(str(n), i[0], i[1]))
            mycursor.execute('insert into Faculty_Tasks (University_ID, Department_Name, Priority) values ("{}", "{}", {})'.format(i[0], i[1], str(n)))
            n += 1
    except:
        continue

mydb.commit()