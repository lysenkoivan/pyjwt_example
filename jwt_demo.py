from flask import Flask, make_response, jsonify, request
import logging
import datetime
from functools import wraps
import base64
import jwt
import time
from multiprocessing import Pool
from multiprocessing import cpu_count

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET'] = "thisistokensecretkey"


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
    time.sleep(sleep)
    return jsonify({"message": "Used memory are free!"})


@app.route("/cpu-usage/<int:core>")
def cpu_usage(core):
    seconds = request.args.get('time', 15, int)
    pool = Pool(core)
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


@app.route("/auth")
def auth():
    creds = request.authorization
    if creds and base64.b64encode(creds.password.encode('utf-8')) == b'cGFzc3dvcmQ=':
        token = jwt.encode({'user': creds.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=59)},
                           app.config['SECRET'])
        return jsonify({'token': token.decode('utf-8')})

    return make_response("Couldn't authorize", 401, {'WWW-Authenticate': 'Basic realm="Login required"'})


@app.route("/auth/token", methods=['GET', 'POST'])
def auth_token():
    credentials = request.json
    if credentials and base64.b64encode(credentials.get('password').encode('utf-8')) == b'cGFzc3dvcmQ=':
        token = jwt.encode(
            {'user': credentials.get('login'), 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=59)},
            app.config['SECRET'])
        return jsonify({'token': token.decode('utf-8')})

    return jsonify({'Error': 'Could not authorize'})


if __name__ == "__main__":
    app.run(debug=True)
