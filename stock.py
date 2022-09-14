from cmath import nan
import yahoo_fin.stock_info as si

class Stock:

    def __init__(self, ticker, initials) -> None:
        self.ticker = ticker
        self.initials = initials
        self.ebitida = None
        self.close = None
        self.beta = None
        self.dy =None

    def get_quote(self):
        self.close = si.get_quote_data(self.ticker)['regularMarketPreviousClose']

    def get_stats(self):
        df = si.get_stats(self.ticker)
        self.beta = df['Value'].iloc[0]
        self.ebitida = df['Value'].iloc[39]
    
    def get_divyield(self):
        df = si.get_dividends(self.ticker)
        self.dy = df['dividend'].iloc[-1] if df.shape[0] else nan
         
# prio = Stock('prio3.sa', 'PRIO3')
# prio.get_quote()
# prio.get_stats()
# prio.get_divyield()
# print(prio.__dict__)
# print(prio.initials, prio.close)
