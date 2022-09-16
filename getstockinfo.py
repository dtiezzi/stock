import sqlite3
from stock import Stock
import yahoo_fin.stock_info as si
import pickle
import pandas as pd
import pandas_datareader.data as web

stock_dict = {}
conn = sqlite3.connect('stock.db')
cur = conn.cursor()
cur.execute('SELECT * FROM tickers')
res = cur.fetchall()
res.sort()
for n,t in enumerate(res):
    stock_dict[t[1]] = Stock(t[0], t[1])
    stock_dict[t[1]].get_quote()
    stock_dict[t[1]].get_stats()
    stock_dict[t[1]].get_divyield()
    print(f'{n+1} from {len(res)}')
conn.close()

with open('./static/files/stockInfo.pkl', 'wb') as file:
    pickle.dump(stock_dict, file)

ibov = web.get_data_yahoo('^BVSP')
ibov.reset_index(inplace=True)
ibov['Date'] = pd.to_datetime(ibov['Date'])
ibov.to_csv('./static/files/ibov.csv')
