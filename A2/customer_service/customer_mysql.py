import mysql.connector
import os


### CONSTANTS ###
MYSQL_SERVER = os.environ["MYSQL_SERVER"]
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWD = os.environ["MYSQL_PASSWD"]


### SETUP ###
mydb = mysql.connector.connect(
    host=MYSQL_SERVER,
    user=MYSQL_USER,
    password=MYSQL_PASSWD,
)

mycursor = mydb.cursor()


### MAIN LOGIC ###
def init_sequence():
    mycursor.execute("SHOW DATABASES")
    dbs = [d[0] for d in mycursor.fetchall()]
    if "ediss" not in dbs:
        mycursor.execute("CREATE DATABASE ediss")
    mycursor.execute("USE ediss")
    mycursor.execute("SHOW TABLES")
    tables = [t[0] for t in mycursor.fetchall()]

    if "users" not in tables:
        print("Creating new users table...")
        create_users_table()


def cleanup():
    mycursor.execute("SHOW TABLES")
    tables = [t[0] for t in mycursor.fetchall()]

    if "users" in tables:
        print("Dropping existing users table..")
        mycursor.execute("DROP TABLE users")


def create_users_table():
    mycursor.execute(
        "CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, userId VARCHAR(255),"
        " name VARCHAR(255), phone VARCHAR(255), address VARCHAR(255),"
        " address2 VARCHAR(255), city VARCHAR(255), state VARCHAR(255),"
        " zipcode VARCHAR(255))")
    

def insert_user(param):
    try:
        mydb.start_transaction()
        print("got transaction for users")
        check_sql = "SELECT * FROM users WHERE userId=%s"
        mycursor.execute(check_sql,[param["userId"]])

        result = mycursor.fetchall()
        print(result)
        if not bool(result):
            sql = "INSERT INTO users (userId, name, phone, address, address2, "\
                    "city, state, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (param["userId"], param["name"], param["phone"], 
                        param["address"], param["address2"], param["city"],
                        param["state"], param["zipcode"])
            mycursor.execute(sql,val)
            mydb.commit()
            id = mycursor.lastrowid
            return id
        else:
            mydb.rollback()
            return False
    except Exception as e:
        mydb.rollback()
        print(e)
        return False
    

def get_user(value, by="id"):
    dict_cursor = mydb.cursor(dictionary=True)
    sql = f"SELECT * FROM users WHERE {by}=%s"
    dict_cursor.execute(sql, [value])
    result = dict_cursor.fetchall()
    dict_cursor.close()

    return result


init_sequence()