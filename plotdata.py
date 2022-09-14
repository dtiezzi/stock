import pandas as pd
import pandas_datareader.data as web
import plotly.express as px

ibov = web.get_data_yahoo('^BVSP')
ibov.reset_index(inplace=True)
print(ibov.head())
ibov['Date'] = pd.to_datetime(ibov['Date'])
print(ibov.columns)

X = ibov['Date'].to_list()
y = ibov['Close'].to_list()

fig = px.line(x=X, y=y, title='IBOV')
fig.show()
