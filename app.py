from flask import Flask
import yahoo_fin.stock_info as si
import sqlite3
import os
import time

app = Flask(__name__)

conn = sqlite3.connect('stock.db')
print('CONNECTED!') if conn else print('ERR!')

@app.route('/')
def index():
    return 'Hello App!'

if __name__ == '__main__':
    app.run()