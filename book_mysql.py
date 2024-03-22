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




def init_sequence():
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS ediss")
    mycursor.execute("USE ediss")
    mycursor.execute("SHOW TABLES")
    tables = [t[0] for t in mycursor.fetchall()]

    if "books" not in tables:
        print("Creating new books table...")
        create_books_table()

    if "users" not in tables:
        print("Creating new users table...")
        create_users_table()

    mycursor.close()
    


def cleanup():
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES")
    tables = [t[0] for t in mycursor.fetchall()]

    if "books" in tables:
        print("Dropping existing books table..")
        mycursor.execute("DROP TABLE books")

    if "users" in tables:
        print("Dropping existing users table..")
        mycursor.execute("DROP TABLE users")
    mycursor.close()


def create_books_table():
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE books (ISBN VARCHAR(255) PRIMARY KEY, title VARCHAR(255),"
                                     " Author VARCHAR(255), description VARCHAR(255), genre VARCHAR(255),"
                                     " price FLOAT(2), quantity INT)")
    mycursor.close()
    

def create_users_table():
    mycursor = mydb.cursor()
    mycursor.execute(
        "CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, userId VARCHAR(255),"
        " name VARCHAR(255), phone VARCHAR(255), address VARCHAR(255),"
        " address2 VARCHAR(255), city VARCHAR(255), state VARCHAR(255),"
        " zipcode VARCHAR(255))")
    mycursor.close()


def insert_book(param):
    mycursor = mydb.cursor()
    sql = "INSERT INTO books (ISBN, title, Author, description, genre, price, quantity)"\
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (param["ISBN"], param["title"], param["Author"], 
            param["description"], param["genre"], param["price"], param["quantity"])
    mycursor.execute(sql,val)


    mydb.commit()
    mycursor.close()


def insert_user(param):
    mycursor = mydb.cursor()
    sql = "INSERT INTO users (userId, name, phone, address, address2, "\
            "city, state, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (param["userId"], param["name"], param["phone"], 
                param["address"], param["address2"], param["city"],
                param["state"], param["zipcode"])
    mycursor.execute(sql,val)
    mydb.commit()
    id = mycursor.lastrowid
    mycursor.close()
    return id


def get_book_isbn(isbn):
    dict_cursor = mydb.cursor(dictionary=True)
    sql = "SELECT * FROM books WHERE ISBN=%s"
    dict_cursor.execute(sql, [isbn])
    result = dict_cursor.fetchall()
    dict_cursor.close()

    return result


def get_user(value, by="id"):
    dict_cursor = mydb.cursor(dictionary=True)
    sql = f"SELECT * FROM users WHERE {by}=%s"
    dict_cursor.execute(sql, [value])
    result = dict_cursor.fetchall()
    dict_cursor.close()

    return result


def update_book_isbn(isbn, param):
    mycursor = mydb.cursor()
    sql = "UPDATE books SET ISBN=%s, title=%s, Author=%s, "\
        "description=%s, genre=%s, price=%s, quantity=%s "\
        "WHERE ISBN=%s"
    val = (param["ISBN"], param["title"], param["Author"], 
                param["description"], param["genre"], param["price"], 
                param["quantity"], isbn)
    
    mycursor.execute(sql,val)
    mydb.commit()
    mycursor.arraysize()


init_sequence()


# def show_books():
#     sql = "SELECT * FROM books LIMIT 5"
#     mycursor.execute(sql)

#     x = mycursor.fetchall()
#     print(x)


# def show_users():
#     sql = "SELECT * FROM users LIMIT 5"
#     mycursor.execute(sql)

#     x = mycursor.fetchall()
#     print(x)



# if __name__ == "__main__":
#     init_sequence()
#     book = {
#             "ISBN": "978-0321815736",
#             "title": "Software Architecture in Practice",
#             "Author": "Bass, L.",
#             "description": "seminal book on software architecture",
#             "genre": "non-fiction",
#             "price": 59.95,
#             "quantity": 106
#     }
#     insert_book(book)

#     user = {
#         "userId": "starlord2002@gmail.com",
#         "name": "Star Lord",
#         "phone": "+14122144122",
#         "address": "48 Galaxy Rd",
#         "address2": "suite 4",
#         "city": "Fargo",
#         "state": "ND",
#         "zipcode": "58102"
#     }
#     insert_user(user)
#     show_books()
#     show_users()

#     cleanup()
#     init_sequence()
    