import yahoo_fin.stock_info as si

class Stock:

    def __init__(self, ticker, initials) -> None:
        self.ticker = ticker
        self.initials = initials
        self.ebitida = None
        self.close = None
        self.beta = None

    def get_quote(self):
        self.close = si.get_quote_data(self.ticker)['regularMarketPreviousClose']

    def get_stats(self):
        self.beta = si.get_stats(self.ticker)['Value'].iloc[0]
        self.ebitida = si.get_stats(self.ticker)['Value'].iloc[39]
         
# prio = Stock('prio3.sa', 'PRIO3')
# prio.get_quote()
# prio.get_stats()
# print(prio.__dict__)
# print(prio.initials, prio.close)
