from flask import Flask, render_template, url_for, redirect, request, session
import yahoo_fin.stock_info as si
import sqlite3
import os
import time
from dotenv import load_dotenv
import pickle
import pandas_datareader.data as web
import pandas as pd
import plotly.express as px
import json
import plotly

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    with open("./static/files/stockInfo.pkl", "rb") as file:
        stock_dict = pickle.load(file)
    l = list(time.localtime())
    date = f'{l[2]}/{l[1]}/{l[0]} - {l[3]}:{l[4]}'
    return render_template('index.html', stocks=stock_dict, date=date)

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
                ibov = web.get_data_yahoo('^BVSP')
                ibov.reset_index(inplace=True)
                print(ibov.head())
                ibov['Date'] = pd.to_datetime(ibov['Date'])
                print(ibov.columns)

                X = ibov['Date'].to_list()
                y = ibov['Close'].to_list()

                fig = px.line(x=X, y=y, title='IBOV')
                div = fig.to_html(full_html=False)
                myShares = {'PRIO3': {'average_val': 26.2, 'actual_val': 26.2, 'yield': 12.1}}
                return render_template('user.html', user=session.user, myShares=myShares, figure = [div])
            else:
                return render_template('signup.html')
        else:
            return render_template('signup.html')
    else:
        return render_template('signup.html')

@app.route('/addshare', methods=['POST'])
def addshare():
    ticker = request.form.get('ticker')
    broker = request.form.get('broker')
    purchase_val = request.form.get('purchase_val')
    quant = request.form.get('quant')
    purchase_dt = request.form.get('purchase-dt')
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    # cur.execute(f"SELECT id FROM users WHERE username = '{session.user}'")
    # user_id = cur.fetchone()[0]
    # cur.execute(f"SELECT id FROM brokers WHERE st_name = '{broker}'")
    # broker_id = cur.fetchone()[0]
    cur.execute(f"SELECT ticker FROM tickers WHERE initials = '{ticker}'")
    ticker = cur.fetchone()[0]
    # cur.execute(f"INSERT INTO holding (user_id, ticker, broker_id, purchase_value, quant, purchase_dt) VALUES ('{user_id}', '{ticker}', '{broker_id}', '{purchase_val}', '{quant}', '{purchase_dt}')")
    conn.commit()
    conn.close()
    print(ticker, broker, purchase_val, quant, purchase_dt)
    return redirect(url_for('user'))

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
        with open("./static/files/stockInfo.pkl", "rb") as file:
            stock_dict = pickle.load(file)
        l = list(time.localtime())
        date = f'{l[2]}/{l[1]}/{l[0]} - {l[3]}:{l[4]}'
        return render_template('index.html', stocks=stock_dict, date=date)
    else:
        return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        with open("./static/files/stockInfo.pkl", "rb") as file:
            stock_dict = pickle.load(file)
        l = list(time.localtime())
        date = f'{l[2]}/{l[1]}/{l[0]} - {l[3]}:{l[4]}'
        return render_template('index.html', stocks=stock_dict, date=date)
    else:
        return render_template('user.html')

if __name__ == '__main__':
    app.run()