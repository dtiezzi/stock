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

def calc(id):
    conn = sqlite3.connect('stock.db')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM holding WHERE user_id = '{id}'")
    res = cur.fetchall()
    if not res:
        df_quote = pd.DataFrame()
        df_quote.to_csv(f'./static/files/my_investiments_{id}.csv')
    else:
        # myShares = {f"{t[2].split('.')[0].upper()}:{t[3]}": {'broker': t[3], 'purchase_val': t[4], 'quant': t[5], 'purchase_dt': t[6], 'ticker': t[2]} for t in res if t[-1] == 'true'}
        myShares = {f"{t[2].split('.')[0].upper()}:{t[3]}": {'id': t[0], 'broker': t[3], 'purchase_val': t[4], 'quant': t[5], 'purchase_dt': t[6], 'ticker': t[2], 'active': True if t[7] == 'true' else False} for t in res}
        for k in myShares:
            myShares[k]['current_val'] = round(si.get_live_price(myShares[k]['ticker']),2)
            myShares[k]['total_val'] = round(myShares[k]['current_val']*myShares[k]['quant'],1)
            myShares[k]['yield'] = round((myShares[k]['current_val']/myShares[k]['purchase_val']-1)*100,1)

        holding_list = [(myShares[k]['ticker'], myShares[k]['id'], myShares[k]['purchase_val'], myShares[k]['purchase_val']*myShares[k]['quant'], myShares[k]['quant'], myShares[k]['purchase_dt'], myShares[k]['current_val'], myShares[k]['current_val']*myShares[k]['quant'], myShares[k]['active']) for k in myShares]

        df = pd.DataFrame(holding_list, columns=['ticker', 'id', 'val', 'purchase_val', 'quant', 'purchase_dt', 'cval', 'current_val','active'])
        df['purchase_dt'] = pd.to_datetime(df['purchase_dt'])
        df = df.sort_values('purchase_dt')
        init_dt = df['purchase_dt'].iloc[0]
        print(df.head())

        ticker = df['ticker'].iloc[0]
        df_quote = si.get_data(ticker, start_date=init_dt)
        df_quote = df_quote.iloc[:, [3]]
        df_quote.columns = [ticker]
        df_quote[f'{ticker}_quant'] = 0
        df_quote[f'{ticker}_invest'] = 0

        df_inactives = df[df['active'] == False]
        df_inactives['selling_dt'] = None
        df_inactives['yield'] = None

        # df = df[df['active'] == True]

        cur.execute(f"SELECT * FROM sold")
        res = cur.fetchall()
        soldDict = {s[1]: {'value': s[2], 'quant': s[3], 'date': s[4], 'yield': s[5]} for s in res}
        for n,i in enumerate(df_inactives['id'].values):
            share = soldDict[i]
            df_inactives['quant'].iloc[n] = share['quant']
            df_inactives['selling_dt'].iloc[n] = share['date']
            df_inactives['yield'].iloc[n] = share['yield']

        df_inactives['purchase_val'] = df_inactives['val']*df_inactives['quant']
        df_inactives['current_val'] = df_inactives['cval']*df_inactives['quant']
        df_inactives['selling_dt'] = pd.to_datetime(df_inactives['selling_dt'])

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
        last_dt = df_quote['Date'].iloc[-1]
        today = datetime.datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        if last_dt != today:
            cp_vals = [df_quote[n].iloc[-1] for n in df_quote.columns]
            df_quote.loc[df_quote.shape[0]] = cp_vals
            # df_quote.append(pd.Series(), ignore_index=True)
            df_quote['Date'].iloc[-1] = today
            df_quote['index'].iloc[-1] = today
            print(df_quote.tail())

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


        for n,i in enumerate(df_quote['Date']):
            if i in df_inactives['purchase_dt'].to_list():
                idx = get_index_positions(df_inactives['purchase_dt'].to_list(), i)
                res = df_inactives.iloc[idx]
                for r in range(res.shape[0]):
                    sell_dt = res['selling_dt'].iloc[r]
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

        print(df_inactives.shape)
        for n in range(df_inactives.shape[0]):
            dt = df_inactives['selling_dt'].iloc[n]
            idx = get_index_positions(df_quote['Date'].to_list(), dt)
            sv = df_inactives['purchase_val'].iloc[n]
            print(dt, sv, idx)
            df_quote[f'total_invest'].iloc[idx[0]:] = df_quote[f'total_invest'].iloc[idx[0]:] - sv 
            # cv = res['current_val'].iloc[r]

        df_quote['yield'] = round((df_quote['total_yield'] - df_quote['total_invest']) / df_quote['total_invest'] * 100, 2)

        # print(df_quote.head())

        df_quote.to_csv(f'./static/files/my_investiments_{id}.csv')

# calc('1')

# # initializing date
# init_dt = df['purchase_dt'].iloc[0] 
# # initializing K
# K = datetime.datetime.today() - init_dt

# date_generated = pd.date_range(init_dt, periods=K.days)


# dt_df = pd.DataFrame(date_generated)
# print(dt_df)