from flask import Flask, render_template, url_for, redirect, request, session
import yahoo_fin.stock_info as si
import sqlite3
import os
import time
from dotenv import load_dotenv
import pickle

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    with open("./static/files/stockInfo.pkl", "rb") as file:
        stock_dict = pickle.load(file)
    return render_template('index.html', stocks=stock_dict)

@app.route('/login', methods=['POST'])
def user():
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute(f"SELECT username, passwd FROM users WHERE username = '{user}'")
        res = cur.fetchone()
        if res:
            if res[1] == password:
                session.user = 'dtiezzi'
                return render_template('user.html', user=session.user)
            else:
                return render_template('index.html')
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = sqlite3.connect('stock.db')
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        cur = conn.cursor()
        cur.execute(f"SELECT username FROM users WHERE username = '{user}'")
        res = cur.fetchall()
        if not res:
            cur.execute(f"INSERT INTO users (username, passwd) VALUES ('{user}', '{password}')")
        conn.commit()
        conn.close()
        return render_template('index.html')
    else:
        return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return render_template('index.html')
    else:
        return render_template('user.html')

if __name__ == '__main__':
    app.run()