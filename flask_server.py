"""
В качестве соли используется username. Мб не самое безопасное решение, но работает.
/register input json
{
    "username": "example",
    "password": "example_pwd"
}

/register output json
{
    "status": "success|failed(user already registered)",
    "datetime": "timestamp"
}

/check input json
{
    "username": "example",
    "password": "example_pwd"
}

/check output json
{
    "status": "registered|not registered",
    "username": "example",
    "datetime": "timestamp|empty string"
}
"""

from flask import Flask, request
import sqlite3
from hashlib import md5
from datetime import datetime

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return 'Hello World!'


def _register(json):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (json.get('username', ''),))
        selected = cursor.fetchone()
        if selected:
            return {'status': 'failed', 'datetime': selected[2]}
        dt = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        _hash = md5(f"{json.get('username', '')}{json.get('password', '')}".encode()).hexdigest()
        cursor.execute(f'INSERT INTO users VALUES (?, ?, ?)', (json.get('username', ''), _hash, dt))
        return {'status': 'success', 'datetime': dt}


def _check(json):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        pwd = md5(f'{json.get("username", "")}{json.get("password", "")}'.encode()).hexdigest()
        cursor.execute(f"SELECT * FROM users WHERE username = ? and password = ?", (json.get('username', ''), pwd))
        selected = cursor.fetchone()
        if not selected:
            return {'status': 'not registered', 'username': json.get('username', ''), 'datetime': ''}
        return {'status': 'registered', 'username': selected[0], 'datetime': selected[2]}


@app.route('/register', methods=['POST'])
def register():
    return _register(request.json)


@app.route('/check', methods=['GET', 'POST'])
def check():
    return _check(request.json)


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
