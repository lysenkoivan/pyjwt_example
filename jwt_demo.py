from flask import Flask, make_response, jsonify, request
import logging
import datetime
import base64
import time
import os
from functools import wraps
from multiprocessing import Pool
from multiprocessing import cpu_count
import jwt
from pymongo import MongoClient
from pymongo.errors import OperationFailure


logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET'] = os.getenv("JWT_SECRET", "secret")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': "Token is missing"}), 403

        try:
            data = jwt.decode(token, app.config['SECRET'])
        except:
            return jsonify({'message': "token is invalid!!"}), 403

        return f(*args, **kwargs)

    return decorated


@app.route("/unprotected")
def unprotected():
    return jsonify({"message": "Unprotected!"})


@app.route("/memory-usage/<int:memory>")
def memory_usage(memory):
    memory_usage_temp = bytearray(memory * 1000000)
    sleep = request.args.get('time', 15, int)
    print(f"Allocating {memory} Mbs for {sleep}s")
    time.sleep(sleep)
    return jsonify({"message": "Allocated {} Mbs. Used memory are free!"})


@app.route("/cpu-usage/<int:core>")
def cpu_usage(core):
    seconds = request.args.get('time', 15, int)
    pool = Pool(core)
    print(f"Loading cpu with {core} cores")
    pool.map(timer_loop, [seconds])

    return jsonify({"message": "Used CPU are free! CPU count is " + str(cpu_count())})


def is_completed(start, duration):
    return time.time() > start + duration


def timer_loop(duration):
    start = time.time()
    while not is_completed(start, duration):
        result = sum(range(2 ** 27))


@app.route("/protected")
@token_required
def protected():
    return jsonify({"message": "Valid token!"})


def gen_token(username):
    token = jwt.encode({
            'sub': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=59),
            "iat": time.time(),
            "authorities": ["ROLE_1", "ROLE_2"]
            },
            app.config['SECRET'])
    save_token(username, token)
    return token


def save_token(user, token):
    """
        Username: authuser
        Password: authuserpassword
        Database Name: authtoken
        Connection URL: mongodb://authuser:authuserpassword@mongodb/authtoken
    """
    mhost = os.getenv("DB_HOST", "noenvvarresult")
    if mhost == "noenvvarresult":
        print("DB_HOST is empty or undefined")
        return None
    mdb = os.getenv("DB_NAME")
    muser = os.getenv("DB_USERNAME")
    mpw = os.getenv("DB_PASSWORD")
    try:
        connstr = f"mongodb://{muser}:{mpw}@{mhost}"
        print(connstr)
        client = MongoClient(connstr)
        col = client[mdb].auth
        data = {"user": user, "token": token}
        data.update(jwt.decode(token, app.config['SECRET']))
        col.insert_one(data)
    except OperationFailure as of:
        print(of)


@app.route("/auth")
def auth():
    creds = request.authorization
    if creds and base64.b64encode(creds.password.encode('utf-8')) == b'cGFzc3dvcmQ=':
        token = gen_token(creds.username)
        return jsonify({'token': token.decode('utf-8')})

    return make_response("Couldn't authorize", 401, {'WWW-Authenticate': 'Basic realm="Login required"'})


@app.route("/auth/token", methods=['GET', 'POST'])
def auth_token():
    credentials = request.json
    if credentials and base64.b64encode(credentials.get('password').encode('utf-8')) == b'cGFzc3dvcmQ=':
        token = gen_token(credentials.get('login'))
        return jsonify({'token': token.decode('utf-8')})

    return jsonify({'Error': 'Could not authorize'}), 401


if __name__ == "__main__":
    app.run()
