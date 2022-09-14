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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    st_name CHAR(11)
);

CREATE TABLE holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    ticker CHAR(11),
    broker_id INTEGER,
    purchase_value NUMERIC,
    quant INTEGER,
    purchase_dt DATE,
    fg_active BOOL,
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
    FOREIGN KEY (holding_id) REFERENCES holding(id)
);