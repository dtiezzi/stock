from numpy import size
import yahoo_fin.stock_info as si
import sqlite3
import pandas as pd
import datetime
import plotly.express as px

def get_index_positions(list_of_elems, element):
    ''' Returns the indexes of all occurrences of give element in
    the list- listOfElements '''
    index_pos_list = []
    index_pos = 0
    while True:
        try:
            # Search for item in list from indexPos to the end of list
            index_pos = list_of_elems.index(element, index_pos)
            # Add the index position in list
            index_pos_list.append(index_pos)
            index_pos += 1
        except ValueError as e:
            break
    return index_pos_list

conn = sqlite3.connect('stock.db')
cur = conn.cursor()
cur.execute(f"SELECT * FROM holding WHERE user_id = '1'")
res = cur.fetchall()
myShares = {f"{t[2].split('.')[0].upper()}:{t[3]}": {'broker': t[3], 'purchase_val': t[4], 'quant': t[5], 'purchase_dt': t[6], 'ticker': t[2]} for t in res if t[-1] == 'true'}
for k in myShares:
    myShares[k]['current_val'] = round(si.get_live_price(myShares[k]['ticker']),2)
    myShares[k]['total_val'] = round(myShares[k]['current_val']*myShares[k]['quant'],1)
    myShares[k]['yield'] = round((myShares[k]['current_val']/myShares[k]['purchase_val']-1)*100,1)

holding_list = [(myShares[k]['ticker'] ,myShares[k]['purchase_val']*myShares[k]['quant'], myShares[k]['quant'], myShares[k]['purchase_dt'], myShares[k]['current_val']*myShares[k]['quant']) for k in myShares]

df = pd.DataFrame(holding_list, columns=['ticker', 'purchase_val', 'quant', 'purchase_dt', 'current_val'])
df['purchase_dt'] = pd.to_datetime(df['purchase_dt'])
df = df.sort_values('purchase_dt')

init_dt = df['purchase_dt'].iloc[0]

ticker = df['ticker'].iloc[0]
df_quote = si.get_data(ticker, start_date=init_dt)
df_quote = df_quote.iloc[:, [3]]
df_quote.columns = [ticker]
df_quote[f'{ticker}_quant'] = 0
df_quote[f'{ticker}_invest'] = 0

for t in df['ticker']:
    if t in df_quote.columns:
        continue
    tmp = si.get_data(t, start_date=init_dt)
    tmp = tmp.iloc[:, [3]]
    tmp.columns = [t]
    tmp[f'{t}_quant'] = 0
    tmp[f'{t}_invest'] = 0
    df_quote = df_quote.merge(tmp, left_index=True, right_index=True)

df_quote.reset_index(inplace=True)
df_quote['Date'] = pd.to_datetime(df_quote['index'])

for n,i in enumerate(df_quote['Date']):
    if i in df['purchase_dt'].to_list():
        idx = get_index_positions(df['purchase_dt'].to_list(), i)
        res = df.iloc[idx]
        for r in range(res.shape[0]):
            tk = res['ticker'].iloc[r]
            q = res['quant'].iloc[r]
            pv = res['purchase_val'].iloc[r]
            qt = q + df_quote[f'{tk}_quant'].iloc[n-1]
            pvt = pv + df_quote[f'{tk}_invest'].iloc[n-1]
            df_quote[f'{tk}_quant'].iloc[n:] = qt
            df_quote[f'{tk}_invest'].iloc[n:] = pvt
            # cv = res['current_val'].iloc[r]

for c in [col for col in df_quote.columns if col.endswith('sa')]:
    df_quote[f'{c}_total'] = df_quote[c] * df_quote[f'{c}_quant']

df_quote['total_yield'] = df_quote[[i for i in df_quote.columns if '_total' in i]].sum(axis=1)
df_quote['total_invest'] = df_quote[[i for i in df_quote.columns if 'invest' in i]].sum(axis=1)

df_quote['yield'] = round((df_quote['total_yield'] - df_quote['total_invest']) / df_quote['total_invest'] * 100, 2)

df_quote.to_csv('./static/files/my_investiments.csv')


# # initializing date
# init_dt = df['purchase_dt'].iloc[0] 
# # initializing K
# K = datetime.datetime.today() - init_dt

# date_generated = pd.date_range(init_dt, periods=K.days)


# dt_df = pd.DataFrame(date_generated)
# print(dt_df)