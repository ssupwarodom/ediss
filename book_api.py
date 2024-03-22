from flask import Flask, request, make_response, abort
import book_mysql
from email_validator import validate_email
import urllib.parse


BOOK_REQUIRED_PARAM = ["ISBN", "title", "Author", "description", 
                           "genre", "price", "quantity"]
USER_REQUIRED_PARAM = ["userId", "name", "phone", "address",
                       "city", "state", "zipcode"]
US_STATES = [
    # https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States#States.
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA",
    "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO",
    "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI",
    "WV", "WY",
]

app = Flask(__name__)


def init_sequence():
    pass


@app.route("/")
def hello():
    return "Hello World"


@app.route("/books", methods=["POST"])
def add_book():
    param = request.get_json()
    if not book_input_valid(param):
        abort(400)
    
    add_book_success = book_mysql.insert_book(param)
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


@app.route("/customers", methods=["POST"])
def add_user():
    param = request.get_json()
    if not user_input_valid(param):
        abort(400)

    id = book_mysql.insert_user(param)
    if not id:
        return {"message": "This user ID already exists in the system."}, 422
    
    param["id"] = id
    resp = make_response(param)
    resp.headers["Location"] = request.base_url + "/" + str(param["id"])

    return resp, 201


@app.route("/customers/<id>", methods=["GET"])
@app.route("/customers", methods=["GET"])
def retrieve_user(id=None):
    if id:
        try:
            id = int(id)
        except:
            abort(400)
        result = book_mysql.get_user(id)
    else:
        encoded_userId = request.args.get("userId")
        userId = urllib.parse.unquote(encoded_userId)
        if not is_email(userId):
            abort(400)
        result = book_mysql.get_user(userId, "userId")

    if not result:
        abort(404)
    return result[0], 200



def book_input_valid(param):
    for field in BOOK_REQUIRED_PARAM:
        if field not in param:
            return False
    
    price = param["price"]
    decimal_places = len(str(price).split(".")[-1])

    if not isinstance(price, float) or decimal_places != 2:
        return False
    
    return True


def user_input_valid(param):
    for field in USER_REQUIRED_PARAM:
        if field not in param:
            return False
    
    if (param["state"] not in US_STATES or 
            not is_email(param["userId"])):
        return False
    
    return True


def is_email(email):
    try:
        v = validate_email(email, check_deliverability=False)
    except:
        return False
    return True


def isbn_exist(isbn):
    return bool(book_mysql.get_book_isbn(isbn))


def user_exist(userId):
    return bool(book_mysql.get_user(userId, "userId"))


if __name__ == '__main__':
    init_sequence()
    app.run(port=8080)