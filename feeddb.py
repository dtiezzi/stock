import pandas as pd
import sqlite3

# ibov_df = pd.read_csv('./static/files/ibov_tickers.csv')
# ibov_initials = ibov_df['Cod'].tolist()
# ibov_tickers = [f'{i.lower()}.sa' for i in ibov_initials]

# conn = sqlite3.connect('stock.db')
# cur = conn.cursor()
# for i,j in zip(ibov_tickers, ibov_initials):
#     print(i,j)
#     sql = f"INSERT INTO tickers (ticker, initials) VALUES ('{i}', '{j}')"
#     cur.execute(sql)
# conn.commit()
# conn.close()

conn = sqlite3.connect('stock.db')
cur = conn.cursor()
l = [('XP Investimentos', 'XP'), ('Toro Investimentos', 'Toro'), ('Banco Inter', 'Inter'), ('Clear Corretora', 'Clear'), ('Nu Invest', 'Nu'), ('BTG Pactual', 'BTG')]
for i,j in l:
    sql = f"INSERT INTO brokers (broker_nm, id) VALUES ('{i}', '{j}')"
    cur.execute(sql)
conn.commit()
conn.close()