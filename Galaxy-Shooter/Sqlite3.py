import sqlite3
from sqlite3 import Error

def create_connection(path):
    connection=None
    try:
        connection=sqlite3.connect(path)
        print("Connection to SQLite succesful!")
    except Error as e:
        print(f"The error '{e}' occured")
    return connection

def execute_query(connection, query):
    cursor=connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print(f"Query [{query}] executed successfully")
    except Error as e:
        print(f"The error '{e}' occured")

def execute_read_query(connection, query):
    cursor=connection.cursor()
    try:
        cursor.execute(query)
        result=cursor.fetchall()
        column_names=[description[0] for description in cursor.description]
        return column_names,result
    except Error as e:
        print(f"The error '{e}' occured")







def insert_Values(player,player_Score,player_Time):
    global player_name
    global player_score
    global player_time

    player_name = player
    player_score = player_Score
    player_time = player_Time

    
    insert_Data_To_SQL()


def insert_Data_To_SQL():
    global connection
    sql_insert_users=f"""
    INSERT INTO users (name,score,time)
    values
    ('{player_name}','{player_score}','{player_time}');
    """
    execute_query(connection,sql_insert_users)



def get_Last_Data_From_SQL():
    global connection
    sql_get_Last_Insert=f"""
    SELECT *
    FROM users 
    ORDER BY id 
    DESC LIMIT 1;
    """
    execute_query(connection,sql_get_Last_Insert)

    cname,cusers=execute_read_query(connection,sql_get_Last_Insert)
    return cusers

def get_High_Score():
    global connection

    sql_select_all_users="""
    SELECT * 
    FROM users 
    ORDER BY score DESC
    LIMIT 3;
    """

    cname,cusers=execute_read_query(connection,sql_select_all_users)
    return cusers

player_name = "Player 1"
player_score = 0
player_time = " "

connection=create_connection("mydatabase.sql")
sql_create_users_table="""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    score INTEGER,
    time TEXT
    );
    """
execute_query(connection,sql_create_users_table)