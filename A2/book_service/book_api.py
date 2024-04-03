from flask import Flask, request, make_response, abort
import A1.book_mysql as book_mysql

### CONSTANTS ###
BOOK_REQUIRED_PARAM = ["ISBN", "title", "Author", "description", 
                           "genre", "price", "quantity"]

### SETUP ###
app = Flask(__name__)

### MAIN LOGIC ###
@app.route("/status")
def health_check():
    return "OK"


@app.route("/books", methods=["POST"])
def add_book():
    param = request.get_json()
    if not book_input_valid(param):
        abort(400)
    print("starting books transaction")
    add_book_success = book_mysql.insert_book(param)
    counter = 0
    while not add_book_success:
        add_book_success = book_mysql.insert_book(param)
        if counter == 3:
            break
        counter += 1
    if not add_book_success:
        return {"message": "This ISBN already exists in the system."}, 422
    
    resp = make_response(param)
    resp.headers["Location"] = request.base_url + "/" + param["ISBN"]
    
    return resp, 201


@app.route("/books/<string:isbn>", methods=["PUT"])
def update_book(isbn):
    param = request.get_json()
    if not book_input_valid(param):
        abort(400)
    if not isbn_exist(isbn):
        abort(404)

    book_mysql.update_book_isbn(isbn, param)
    return param, 200


@app.route("/books/isbn/<string:isbn>")
@app.route("/books/<string:isbn>")
def retrieve_book_isbn(isbn):
    book = book_mysql.get_book_isbn(isbn)
    if not book:
        abort(404)

    return book[0], 200


def book_input_valid(param):
    for field in BOOK_REQUIRED_PARAM:
        if field not in param:
            return False
    
    price = param["price"]
    decimal_places = len(str(price).split(".")[-1])

    if not isinstance(price, float) or decimal_places != 2:
        return False
    
    return True


def isbn_exist(isbn):
    return bool(book_mysql.get_book_isbn(isbn))


if __name__ == '__main__':
    app.run(port=8080)