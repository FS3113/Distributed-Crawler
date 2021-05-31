import mysql.connector
import sys
import json
import os


if __name__ == "__main__":
    mydb = mysql.connector.connect(
        host="localhost",
        user="juefeic2",
        password="0202141208",
        database="juefeic2_educationtoday"
    )

    mycursor = mydb.cursor()
    path = ' '.join(sys.argv[1:])
    with open(path) as f:
        data = json.load(f)

    task = data['task']

    if task == 'department':
        mycursor.execute('SELECT University_ID FROM University where University_Name = \"' + data['university'] + '\";')
        university_id = mycursor.fetchone()[0]
        task_id = str(university_id) + data['id']

        sql = 'insert into Department_History (Task_ID, University_ID, Time_Stamp, Execution_Time, URL, Algo_Version, Status) values (%s, %s, %s, %s, %s, %s, %s)'
        vals = (task_id, university_id, data['time_stamp'], data['execution_time'], data['url'], data['algo_version'], data['status'])
        mycursor.execute(sql, vals)

        sql = 'insert into Department (Task_ID, Department_Name) values (%s, %s)'
        for i in data['data']:
            if len(i) > 180:
                continue
            vals = (task_id, i)
            try:
                mycursor.execute(sql, vals)
            except:
                continue
        mydb.commit()
        if os.path.exists(path):
            os.remove(path)

    
    if task == 'faculty':
        mycursor.execute('SELECT University_ID FROM University where University_Name = \"' + data['university'] + '\";')
        university_id = mycursor.fetchone()[0]
        task_id = str(university_id) + data['department'] + data['id']

        sql = 'insert into Faculty_History (Task_ID, University_ID, Department_Name, Time_Stamp, Execution_Time, URL, Algo_Version, Status) values (%s, %s, %s, %s, %s, %s, %s, %s)'
        vals = (task_id, university_id, data['department'], data['time_stamp'], data['execution_time'], data['url'], data['algo_version'], data['status'])
        mycursor.execute(sql, vals)

        sql = 'insert into Faculty (Task_ID, Name, Position, Research, Email, Phone) values (%s, %s, %s, %s, %s, %s)'
        for i in data['data']:
            name, position, research, email, phone = '', '', '', '', ''
            if 'Name' not in i:
                continue
            name = i['Name']
            if len(name) > 200:
                name = name[:200]
            if 'Position' in i:
                position = i['Position']
                if position == 'Missing':
                    position = ''
                if len(position) > 200:
                    position = position[:200]
            if 'Research Interest' in i:
                research = i['Research Interest']
                if research == 'Missing':
                    research = ''
                if len(research) > 400:
                    research = research[:400]
            if 'Email' in i:
                email = i['Email']
                if email == 'Missing':
                    email = ''
                if len(email) > 100:
                    email = email[:100]
            if 'Phone number' in i:
                phone = i['Phone number']
                if phone == 'Missing':
                    phone = ''
                if len(phone) > 100:
                    phone = phone[:100]
            vals = (task_id, name, position, research, email, phone)
            try:
                mycursor.execute(sql, vals)
            except:
                continue
        mydb.commit()
        if os.path.exists(path):
            os.remove(path)