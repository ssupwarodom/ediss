import mysql.connector
import os

MYSQL_SERVER = os.environ["MYSQL_SERVER"]
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWD = os.environ["MYSQL_PASSWD"]


mydb = mysql.connector.connect(
    host=MYSQL_SERVER,
    user=MYSQL_USER,
    password=MYSQL_PASSWD,
)

mycursor = mydb.cursor()

def init_sequence():
    mycursor.execute("SHOW DATABASES")
    dbs = [d[0] for d in mycursor.fetchall()]
    if "ediss" not in dbs:
        mycursor.execute("CREATE DATABASE ediss")
    mycursor.execute("USE ediss")
    mycursor.execute("SHOW TABLES")
    tables = [t[0] for t in mycursor.fetchall()]

    if "books" not in tables:
        print("Creating new books table...")
        create_books_table()


def cleanup():
    mycursor.execute("SHOW TABLES")
    tables = [t[0] for t in mycursor.fetchall()]

    if "books" in tables:
        print("Dropping existing books table..")
        mycursor.execute("DROP TABLE books")


def create_books_table():
    mycursor.execute("CREATE TABLE books (ISBN VARCHAR(255) PRIMARY KEY, title VARCHAR(255),"
                                     " Author VARCHAR(255), description VARCHAR(255), genre VARCHAR(255),"
                                     " price FLOAT(2), quantity INT)")
    

def insert_book(param):
    try:
        mydb.start_transaction()
        print("got transaction for books")
        check_sql = "SELECT * FROM books WHERE ISBN=%s"
        mycursor.execute(check_sql,[param["ISBN"]])

        result = mycursor.fetchall()
        print(result)
        if not bool(result):
            sql = "INSERT INTO books (ISBN, title, Author, description, genre, price, quantity)"\
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (param["ISBN"], param["title"], param["Author"], 
                    param["description"], param["genre"], param["price"], param["quantity"])
            mycursor.execute(sql,val)
            mydb.commit()
        else:
            mydb.rollback()
            return False
    except Exception as e:
        mydb.rollback()
        print(e)
        return False
    
    return True


def get_book_isbn(isbn):
    dict_cursor = mydb.cursor(dictionary=True)
    sql = "SELECT * FROM books WHERE ISBN=%s"
    dict_cursor.execute(sql, [isbn])
    result = dict_cursor.fetchall()
    dict_cursor.close()

    return result


def update_book_isbn(isbn, param):
    sql = "UPDATE books SET ISBN=%s, title=%s, Author=%s, "\
        "description=%s, genre=%s, price=%s, quantity=%s "\
        "WHERE ISBN=%s"
    val = (param["ISBN"], param["title"], param["Author"], 
                param["description"], param["genre"], param["price"], 
                param["quantity"], isbn)
    
    mycursor.execute(sql,val)
    mydb.commit()


init_sequence()