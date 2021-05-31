# import mysql.connector

# mydb = mysql.connector.connect(
#     host="localhost",
#     user="juefeic2",
#     password="0202141208",
#     database="juefeic2_educationtoday"
# )

# mycursor = mydb.cursor()

# mycursor.execute("DROP TABLE IF EXISTS Department_History;")
# mycursor.execute("DROP TABLE IF EXISTS Department;")

# create table tutorials_tbl(
#    tutorial_id INT NOT NULL AUTO_INCREMENT,
#    tutorial_title VARCHAR(100) NOT NULL,
#    tutorial_author VARCHAR(40) NOT NULL,
#    submission_date DATE,
#    PRIMARY KEY ( tutorial_id )
# );

# Task_ID (University_ID + Time_Stamp)
# University_ID
# Time_Stamp
# Execution_Time
# URL
# Algo_Version
# Status (Success / Fail)

# create table Department_History(
#     Task_ID VARCHAR(100) NOT NULL,
#     University_ID int,
#     Time_Stamp VARCHAR(100),
#     Execution_Time int,
#     URL VARCHAR(100),
#     Algo_Version int,
#     Status VARCHAR(20),
#     PRIMARY KEY ( Task_ID )
# );

# create table Department(
#     Task_ID VARCHAR(100) NOT NULL,
#     Department_Name VARCHAR(200)
# );

# create table Faculty_University_Status(
#     University_ID int,
#     University_Name VARCHAR(100),
#     Status VARCHAR(20),
#     PRIMARY KEY (University_ID)
# );

# create table Faculty_Status(
#     University_ID int,
#     Department_Name VARCHAR(200),
#     Status VARCHAR(20)
# );

# create table Faculty_History(
#     Task_ID VARCHAR(300) NOT NULL,
#     University_ID int,
#     Department_Name VARCHAR(200),
#     Time_Stamp VARCHAR(100),
#     Execution_Time int,
#     URL VARCHAR(200),
#     Algo_Version int,
#     Status VARCHAR(20),
#     PRIMARY KEY ( Task_ID )
# );

# create table Faculty(
#     Task_ID VARCHAR(300) NOT NULL,
#     Name VARCHAR(200),
#     Position VARCHAR(200),
#     Research VARCHAR(400),
#     Email VARCHAR(100),
#     Phone VARCHAR(100)
# );
