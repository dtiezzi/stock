from flask import Flask, render_template, url_for, redirect, request, session
from matplotlib import ticker
# from flask_session import Session
import yahoo_fin.stock_info as si
import sqlite3
import os
import time
from dotenv import load_dotenv
import pickle
# import pandas_datareader.data as web
import pandas as pd
import plotly.express as px
import json
import plotly

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    with open("./static/files/stockInfo.pkl", "rb") as file:
        stock_dict = pickle.load(file)
    l = list(time.localtime())
    date = f'{l[2]}/{l[1]}/{l[0]} - {l[3]}:{l[4]}'
    return render_template('index.html', stocks=stock_dict, date=date)

@app.route('/login', methods=['GET','POST'])
def user():
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('stock.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE username = '{user}'")
        res = cur.fetchone()
        if res:
            if res[2] == password:
                session["user"] = user
                session['user_id'] = res[0]
                ibov = pd.read_csv('./static/files/ibov.csv')
                X = ibov['Date'].to_list()
                y = ibov['Close'].to_list()
                fig = px.line(x=X, y=y, title='IBOV')
                global div
                div = fig.to_html(full_html=False)
                cur.execute(f"SELECT * FROM holding WHERE user_id = '{session['user_id']}'")
                res = cur.fetchall()
                myShares = {t[2].split('.')[0].upper(): {'broker': t[3], 'purchase_val': t[4], 'quant': t[5], 'purchase_dt': t[6], 'ticker': t[2]} for t in res}
                for k in myShares:
                    myShares[k]['current_val'] = round(si.get_live_price(myShares[k]['ticker']),2)
                    myShares[k]['total_val'] = round(myShares[k]['current_val']*myShares[k]['quant'],1)
                    myShares[k]['yield'] = round((myShares[k]['current_val']/myShares[k]['purchase_val']-1)*100,1)
                return render_template('user.html', user=session['user'], myShares=myShares, figure = [div])
            else:
                return render_template('signup.html')
        else:
            return render_template('signup.html')
    else:
        if session['user']:
            conn = sqlite3.connect('stock.db')
            cur = conn.cursor()
            res = cur.fetchall()
            myShares = {t[2].split('.')[0].upper(): {'broker': t[3], 'purchase_val': t[4], 'quant': t[5], 'purchase_dt': t[6], 'ticker': t[2]} for t in res}
            for k in myShares:
                myShares[k]['current_val'] = round(si.get_live_price(myShares[k]['ticker']),2)
                myShares[k]['total_val'] = round(myShares[k]['current_val']*myShares[k]['quant'],1)
                myShares[k]['yield'] = round((myShares[k]['current_val']/myShares[k]['purchase_val']-1)*100,1)
            return render_template('user.html', user=session['user'], myShares=myShares, figure = [div])
        return render_template('signup.html')

@app.route('/addshare', methods=['POST'])
def addshare():
    user = session['user']
    ticker = request.form.get('ticker')
    broker = request.form.get('broker')
    purchase_val = request.form.get('purchase_val')
    quant = request.form.get('quant')
    purchase_dt = request.form.get('purchase_dt')
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM users WHERE username = '{user}'")
    user_id = cur.fetchone()[0]
    cur.execute(f"SELECT ticker FROM tickers WHERE initials = '{ticker}'")
    ticker = cur.fetchone()[0]
    cur.execute(f"INSERT INTO holding (user_id, ticker, broker_id, purchase_value, quant, purchase_dt) VALUES ('{user_id}', '{ticker}', '{broker}', '{purchase_val}', '{quant}', '{purchase_dt}')")
    conn.commit()
    conn.close()
    return redirect(url_for('user'))

@app.route('/plotticker', methods=['POST'])
def plotticker():
    ticker = request.form.get('ticker')
    df = si.get_data(ticker)
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['index'])
    X = df['Date'].to_list()
    y = df['close'].to_list()
    fig1 = px.line(x=X, y=y, title=ticker)
    div1 = fig1.to_html(full_html=False)
    return render_template('ticker.html', figure = [div1])


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
        session["name"] = None
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