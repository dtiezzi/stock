import sqlite3
import dotenv
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
IP = os.getenv('IP')
PORT = os.getenv('PORT')

conn = sqlite3.connect('stock.db')
cur = conn.cursor()
cur.execute('SELECT * FROM holding WHERE user_id = 1')
res = cur.fetchall()
print(res)
stk_id = [id[0] for id in res if id[-1] == 'false']
print(stk_id)

sold = []
for i in stk_id:
    cur.execute(f"SELECT * FROM sold WHERE holding_id = '{i}'")
    sold.append(cur.fetchone())

print(sold)

df_holdind = pd.DataFrame(res, columns=['holding_id', 'user_id', 'ticker', 'broker_id', 'purchase_val', 'quant', 'purchase_dt', 'fg_active'])
df_sold = pd.DataFrame(sold, columns=['id', 'holding_id', 'sell_value', 'quant', 'selling_dt', 'yield'])

# print(df_sold)

df = pd.merge(df_holdind, df_sold, on='holding_id',how='left')
print(df)
user = 'dtiezzi'
df.to_csv(f'./static/files/irpf_{user}.csv')
