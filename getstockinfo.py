import imp


import sqlite3
from stock import Stock
import yahoo_fin.stock_info as si
import pickle

stock_dict = {}
conn = sqlite3.connect('stock.db')
cur = conn.cursor()
cur.execute('SELECT * FROM tickers')
res = cur.fetchall()
for t in res:
    stock_dict[t[1]] = Stock(t[0], t[1])
    stock_dict[t[1]].get_quote()
    stock_dict[t[1]].get_stats()
conn.close()

with open('./static/files/stockInfo.pkl', 'wb') as file:
    pickle.dump(stock_dict, file)
