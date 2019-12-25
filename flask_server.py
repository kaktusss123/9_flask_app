"""
В качестве соли используется username. Мб не самое безопасное решение, но работает.
/[GET, POST] - Hello, world!
/users[GET] - возвращает инфу обо всех пользователях
/users[POST](json) - регистрирует пользователя с данными из json {"username": "", "password": ""}
/users/<username>[GET] - возвращает всю информацию о юзере
/check[GET, POST](json) - проверяет наличие в бд пользователя с параметрами {"username": "", "password": ""}
"""

from flask import Flask, request, jsonify
import sqlite3
from hashlib import md5
from datetime import datetime
from typing import Union

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def _help() -> str:
    with open('help.html', 'r', encoding='utf-8') as f:
        return f.read()


def _register(json: dict) -> Union[dict, tuple]:
    """
    Register user in database
    :param json: dict with 'username' and 'password' fields
    :return: status json
    """
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        # Check for user existence
        cursor.execute("SELECT username FROM users WHERE username = ?", (json.get('username', ''),))
        selected = cursor.fetchone()
        if selected:
            return {'status': 'user already exists'}, 400
        # Register new user
        dt = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        _hash = md5("".join((json.get('username', ''), json.get('password', ''))).encode()).hexdigest()
        cursor.execute(f'INSERT INTO users VALUES (?, ?, ?)', (json.get('username', ''), _hash, dt))
        return {'status': 'success', 'datetime': dt}


def _check(json: dict) -> dict:
    """
    Check user existence with 'username' and 'password'
    :param json: dict with 'username' and 'password' fields
    :return: status json
    """
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        pwd = md5(f'{json.get("username", "")}{json.get("password", "")}'.encode()).hexdigest()
        cursor.execute(f"SELECT * FROM users WHERE username = ? and password = ?", (json.get('username', ''), pwd))
        selected = cursor.fetchone()
        if not selected:
            return {'status': 'not registered', 'username': json.get('username', '')}
        return {'status': 'registered', 'username': selected[0], 'datetime': selected[2]}


@app.route('/users', methods=['POST'])
def register() -> Union[dict, tuple]:
    """
    Flask wrapper for _register
    :return:
    """
    # Check for bad request
    if request.json is None or not all([x in request.json for x in ('username', 'password')]):
        return {'status': 'bad request'}, 400
    return _register(request.json)


@app.route('/users/<string:username>', methods=['GET'])
def get_user_by_username(username: str) -> Union[dict, tuple]:
    """
    Get user info by username
    :param username: username?
    :return:
    """
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        selected = cursor.fetchone()
        if selected is None:
            return {'status': 'not found'}, 404
        return dict(zip(('username', 'password_hash', 'datetime'), selected))


@app.route('/users', methods=['GET'])
def get_all_users() -> list:
    """
    Function for getting info about all users
    :return: List of user dicts
    """
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        return jsonify([dict(zip(('username', 'password_hash', 'datetime'), x)) for x in cursor.fetchall()])


@app.route('/check', methods=['GET', 'POST'])
def check() -> Union[dict, tuple]:
    """
    Flask wrapper for _check
    :return:
    """
    # Check for bad request
    if request.json is None or not all([x in request.json for x in ('username', 'password')]):
        return {'status': 'bad request'}, 400
    return _check(request.json)


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
