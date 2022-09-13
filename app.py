from flask import Flask
import yahoo_fin.stock_info as si
import os
import time

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello App!'

if __name__ == '__main__':
    app.run()