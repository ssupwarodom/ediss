from flask import Flask, request, abort
import jwt
from datetime import datetime
import requests
import os


### CONSTANTS ###
BACKEND_URL = os.environ["BACKEND_URL"] + ":3000/"
SUB_ALLOWED = ["starlord", "gamora", "drax", "rocket", "groot"]
ISS_ALLOWED = ["cmu.edu"]
METHODS = {
    "GET": requests.get,
    "POST": requests.post,
    "PUT": requests.put
}
TEST_RSP = {
    "genre": "non-fiction",
    "address": "1234",
    "name": "Pat"
}

### SETUP ###
app = Flask(__name__)

### MAIN LOGIC ###
@app.route("/status")
@app.route("/")
def health_check():
    return "OK"


@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    if not request.headers.get("Authorization"):
        abort(400)
    
    token = request.headers.get("Authorization").split()[-1]
    if not valid_jwt(token):
        abort(401)

    response = METHODS[request.method](
        BACKEND_URL+path,
        json=request.get_json(),
        headers=request.headers
    )
    
    try:
        rsp = response.json()
    except:
        return {}, response.status_code


    if request.method == "GET" and path.startswith("books"):
        if rsp["genre"] == "non-fiction":
            rsp["genre"] = 3
    elif request.method == "GET" and path.startswith("customers"):
        for key in ["address", "address2", "city", "state", "zipcode"]:
            rsp.pop(key, None)

    return rsp, response.status_code


def valid_jwt(token):
    # Decode and catch malformed jwt token
    try:
        decoded_token = jwt.decode(token, algorithms=['HS256'], 
                                   options={'verify_signature': False})
        expiry = datetime.fromtimestamp(decoded_token["exp"])
    except:
        return False
    
    # Check for invalid conditions
    if (decoded_token["sub"] not in SUB_ALLOWED
            or decoded_token["iss"] not in ISS_ALLOWED
            or expiry < datetime.now()):
        return False
    
    return True


if __name__ == '__main__':
    app.run(port=80)