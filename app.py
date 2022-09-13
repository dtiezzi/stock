from flask import Flask, render_template, url_for, redirect, request, session
import yahoo_fin.stock_info as si
import sqlite3
import os
import time
from dotenv import load_dotenv
from stock import Stock

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def user():
    conn = sqlite3.connect('stock.db')
    print('CONNECTED!') if conn else print('ERR!')
    if request.method == 'POST':
        session.user = 'dtiezzi'
        return render_template('user.html', user=session.user)
    else:
        conn.close()
        return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = sqlite3.connect('stock.db')
    if request.method == 'POST':
        return render_template('index.html', user=session.user)
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