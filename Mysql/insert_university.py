import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="juefeic2",
    password="0202141208",
    database="juefeic2_educationtoday"
)

mycursor = mydb.cursor()

# sql = "INSERT INTO University (University_ID, University_Name) VALUES (%s, %s)"

# f = open('US_Universities.txt', 'r')
# a = 1
# for i in f.readlines():
#     i = i[:-1]
#     print(i)
#     val = (a, i)
#     mycursor.execute(sql, val)
#     a += 1

# mydb.commit()
