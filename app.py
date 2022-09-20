from cv2 import denoise_TVL1
from flask import Flask, render_template, url_for, redirect, request, session
from matplotlib import ticker
import yahoo_fin.stock_info as si
import sqlite3
import os
import time
from dotenv import load_dotenv
import pickle
import pandas as pd
import plotly.express as px
from plotyield import plotyield, plotvalues

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
IP = os.getenv('IP')
PORT = os.getenv('PORT')

@app.route('/')
def index():
    with open("./static/files/stockInfo.pkl", "rb") as file:
        stock_dict = pickle.load(file)
    l = list(time.localtime())
    date = f'{l[2]}/{l[1]}/{l[0]} - {l[3]}:{l[4]}'
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute('SELECT id, ticker FROM holding')
    res = cur.fetchall()
    res.sort()
    ids_dict = {i[0]: i[1] for i in res}
    with open('./static/files/idstickers.pkl', 'wb') as file:
        pickle.dump(ids_dict, file)
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
                fig = px.line(ibov, x='Date', y='Close', labels={
                     "Close": "Valor",
                     "Date": "Data"
                 }, title='Cotação IBOV')
                global div
                div = fig.to_html(full_html=False)
                global div1
                df_quote = pd.read_csv('./static/files/my_investiments.csv')
                div1 = plotyield(df_quote).to_html(full_html=False)
                div2 = plotvalues(df_quote).to_html(full_html=False)
                global ids_dict
                with open("./static/files/idstickers.pkl", "rb") as file:
                    ids_dict = pickle.load(file)
                cur.execute(f"SELECT * FROM holding WHERE user_id = '{session['user_id']}'")
                res = cur.fetchall()
                myShares = {f"{t[2].split('.')[0].upper()}:{t[3]}": {'broker': t[3], 'purchase_val': t[4], 'quant': t[5], 'purchase_dt': t[6], 'ticker': t[2]} for t in res if t[-1] == 'true'}
                for k in myShares:
                    myShares[k]['current_val'] = round(si.get_live_price(myShares[k]['ticker']),2)
                    myShares[k]['total_val'] = round(myShares[k]['current_val']*myShares[k]['quant'],1)
                    myShares[k]['yield'] = round((myShares[k]['current_val']/myShares[k]['purchase_val']-1)*100,1)
                holding_ids = [h[0] for h in res]
                cur.execute("SELECT * FROM sold")
                res = cur.fetchall()
                l = list(time.localtime())
                month = str(l[1]) if len(str(l[1])) == 2 else f'0{str(l[1])}'
                sold_month = [list(s) for s in res if s[1] in holding_ids and s[4].split('-')[1] == month]
                for s in sold_month:
                    s[1] = ids_dict[s[1]].split('.')[0].upper()
                total = round(sum([v[2]*v[3] for v in sold_month]),2)
                yield_month = round(sum([v[-1] for v in sold_month]),2)
                return render_template('user.html', user=session['user'], myShares=myShares, figure = [div], figure1 = [div1, div2], sold=sold_month, total=total, yield_month=yield_month)
            else:
                return render_template('signup.html')
        else:
            return render_template('signup.html')
    else:
        if session['user']:
            conn = sqlite3.connect('stock.db')
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM holding WHERE user_id = '{session['user_id']}'")
            res = cur.fetchall()
            myShares = {f"{t[2].split('.')[0].upper()}:{t[3]}": {'broker': t[3], 'purchase_val': t[4], 'quant': t[5], 'purchase_dt': t[6], 'ticker': t[2]} for t in res if t[-1] == 'true'}
            for k in myShares:
                myShares[k]['current_val'] = round(si.get_live_price(myShares[k]['ticker']),2)
                myShares[k]['total_val'] = round(myShares[k]['current_val']*myShares[k]['quant'],1)
                myShares[k]['yield'] = round((myShares[k]['current_val']/myShares[k]['purchase_val']-1)*100,1)
            # shares_summary = []
            holding_ids = [h[0] for h in res]
            cur.execute("SELECT * FROM sold")
            res = cur.fetchall()
            l = list(time.localtime())
            month = str(l[1]) if len(str(l[1])) == 2 else f'0{str(l[1])}'
            sold_month = [list(s) for s in res if s[1] in holding_ids and s[4].split('-')[1] == month]
            for s in sold_month:
                s[1] = ids_dict[s[1]].split('.')[0].upper()
            total = round(sum([v[2]*v[3] for v in sold_month]),2)
            yield_month = round(sum([v[-1] for v in sold_month]),2)
            return render_template('user.html', user=session['user'], myShares=myShares, figure = [div], figure1 = [div1, div2], sold=sold_month, total=total, yield_month=yield_month)
        return render_template('signup.html')

@app.route('/addshare', methods=['POST'])
def addshare():
    user = session['user']
    ticker = request.form.get('ticker')
    broker = request.form.get('broker')
    purchase_val = float(request.form.get('purchase_val'))
    quant = int(request.form.get('quant'))
    purchase_dt = request.form.get('purchase_dt')
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM users WHERE username = '{user}'")
    user_id = cur.fetchone()[0]
    cur.execute(f"SELECT ticker FROM tickers WHERE initials = '{ticker}'")
    print(ticker)
    ticker = cur.fetchone()[0]
    cur.execute(f"SELECT * FROM holding WHERE user_id = '{user_id}' AND ticker = '{ticker}' AND broker_id = '{broker}'")
    res = cur.fetchone()
    if res:
        original_val = float(res[4])
        original_quant = int(res[5])
        purchase_val = round((original_val*original_quant + purchase_val*quant)/(original_quant+quant),2)
        quant = quant + original_quant
        cur.execute(f"UPDATE holding SET purchase_value = '{purchase_val}', quant = '{quant}' WHERE user_id = '{user_id}' AND ticker = '{ticker}' AND broker_id = '{broker}'")
    else:
        cur.execute(f"INSERT INTO holding (user_id, ticker, broker_id, purchase_value, quant, purchase_dt) VALUES ('{user_id}', '{ticker}', '{broker}', '{purchase_val}', '{quant}', '{purchase_dt}')")
    conn.commit()
    conn.close()
    return redirect(url_for('user'))

@app.route('/sellshare', methods=['POST'])
def sellshare():
    user = session['user']
    ticker = request.form.get('ticker')
    broker = request.form.get('broker')
    selling_val = float(request.form.get('selling_val'))
    quant = int(request.form.get('quant'))
    selling_dt = request.form.get('selling_dt')
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM users WHERE username = '{user}'")
    user_id = cur.fetchone()[0]
    cur.execute(f"SELECT ticker FROM tickers WHERE initials = '{ticker}'")
    ticker = cur.fetchone()[0]
    cur.execute(f"SELECT * FROM holding WHERE user_id = '{user_id}' AND ticker = '{ticker}' AND broker_id = '{broker}'")
    res = cur.fetchone()
    if res:
        holding_id = res[0]
        original_quant = int(res[5])
        yield_val = round((selling_val*quant) - (float(res[4])*quant),2)
        cur.execute(f"INSERT INTO sold (holding_id, sell_value, quant, selling_dt, yield) VALUES ('{holding_id}', '{selling_val}', '{quant}', '{selling_dt}', '{yield_val}')")
        if quant == original_quant:
            cur.execute(f"UPDATE holding SET quant = 0, fg_active = 'false' WHERE id = '{holding_id}';")
        else:
            quant = original_quant - quant
            cur.execute(f"UPDATE holding SET quant = {quant} WHERE id = '{holding_id}';")
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
    return render_template('ticker.html', ticker=ticker, figure=[div1])

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
    