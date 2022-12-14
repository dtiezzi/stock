CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username CHAR(21),
    passwd CHAR(36)
);

CREATE TABLE tickers (
    ticker CHAR(11) PRIMARY KEY NOT NULL,
    initials CHAR(9)
);

CREATE TABLE brokers (
    id CHAR(11) PRIMARY KEY,
    broker_nm TEXT,
    
);

CREATE TABLE holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    ticker CHAR(11),
    broker_id CHAR(11),
    purchase_value NUMERIC,
    quant INTEGER,
    purchase_dt DATE,
    fg_active BOOL DEFAULT true,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (ticker) REFERENCES tickers(ticker),
    FOREIGN KEY (broker_id) REFERENCES brokers(id)
);

CREATE TABLE sold (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    holding_id INTEGER,
    sell_value NUMERIC,
    quant INTEGER,
    selling_dt DATE,
    yield NUMERIC,
    FOREIGN KEY (holding_id) REFERENCES holding(id)
);

CREATE TABLE mylist (
    ticker CHAR(11),
    user_id INTEGER,
    fg_active BOOL DEFAULT true,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (ticker) REFERENCES tickers(ticker)
);