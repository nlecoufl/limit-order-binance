#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 10:29:21 2020

@author: nicolas
"""
import time
import json
import hmac
import hashlib
import requests
import sqlite3
import os
from sqlite3 import Error
from urllib.parse import urljoin, urlencode

exchangeName='Binance'

BASE_URL = 'https://api.binance.com'
API_KEY = os.environ.get("PUBLIC_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")

headers = {
    'X-MBX-APIKEY': API_KEY
}

class BinanceException(Exception):
    def __init__(self, status_code, data):

        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"

        # Python 2.x
        # super(BinanceException, self).__init__(message)
        super().__init__(message)

def getList():
    PATH = '/api/v3/ticker/price'
    params = {}
    
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
        
def getDepth(direction='ask',pair='BTCUSDT'):
    PATH = '/api/v1/depth'
    params = {
        'symbol' : pair,
        'limit' : 5
    }
    
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
        
    if r.status_code == 200:
        if (direction == 'ask'):
            print(json.dumps(removeKey(r.json(),'bids'), indent=2))
        else:
            print(json.dumps(removeKey(r.json(),'asks'), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())

def removeKey(d, key):
    r = dict(d)
    del r[key]
    return r

def getOrderBook(pair='BTCUSDT'):
    PATH = '/api/v1/depth'
    params = {
        'symbol': pair,
        'limit': 5
    }
    
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
        
def refreshDataCandle(pair = 'BTCUSDT',duration = '5m'):
    PATH = '/api/v3/klines'
    params = {
        'symbol' : pair,
        'interval' : duration
    }
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    con = sqlConnection()
    c=con.cursor()
    setTableName = str(exchangeName + "_" + pair + "_"+ duration)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
        c.executemany('INSERT INTO ' + setTableName + ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', r.json())
        con.commit()
        con.close()
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())

def sqlConnection():
    try:
        con = sqlite3.connect('datas.db')
        return con
    except Error:
        print(Error)
        
def createCandleTable(con,pair,duration):
    cursorObj = con.cursor()
    
    setTableName = str(exchangeName + "_" + pair + "_"+ duration)
    tableCreationStatement = """CREATE TABLE """ + setTableName + """(opentime
    INT, open REAL, high REAL, low REAL, close REAL,volume REAL, closetime int, quotevolume
    REAL, numberoftrade REAL, takerbuybaseassetvolume REAL, tokerbuyquoteassetvolume REAL, ignore REAL)"""
    cursorObj.execute(tableCreationStatement)
    con.commit()
    con.close()
    
def createTradeTable(con,pair):
    cursorObj = con.cursor()
    
    setTableName = str(exchangeName + "_" + pair)
    tableCreationStatement = """CREATE TABLE """ + setTableName + """(aggregateTradeID
    INT, price REAL, qty REAL, firstTradeID INT, lastTradeID INT, timestamp INT, 
    wasBuyerMaker BOOL, wasTradeBestPriceMatch BOOL)"""
    cursorObj.execute(tableCreationStatement)
    con.commit()
    con.close()

def refreshData(pair = 'BTCUSDT'):
    PATH = '/api/v3/aggTrades'
    params = {
        'symbol' : pair
    }
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    con = sqlConnection()
    c=con.cursor()
    setTableName = str(exchangeName + "_" + pair)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
        l=[]
        for i in range(len(r.json())):
            temp=[]
            for valeur in r.json()[i].values():
                temp.append(valeur)
            l.append(temp)
        c.executemany('INSERT INTO ' + setTableName + ' VALUES (?,?,?,?,?,?,?,?)', l)
        con.commit()
        con.close()
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())  
        
def createOrder(direction, price, amount, pair = 'BTCUSDT', orderType = 'LIMIT'):
    PATH = '/api/v3/order'
    timestamp = int(time.time() * 1000)
    params = {
        'symbol': pair,
        'side': direction,
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': amount,
        'price': price,
        'recvWindow': 5000,
        'timestamp': timestamp
    }
    
    query_string = urlencode(params)
    params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    url = urljoin(BASE_URL, PATH)
    r = requests.post(url, headers=headers, params=params)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
        
def cancelOrder(uuid, pair='BTCUSDT'):  
    PATH = '/api/v3/order'
    timestamp = int(time.time() * 1000)
    params = {
        'symbol': pair,
        'orderId': uuid,
        'recvWindow': 5000,
        'timestamp': timestamp
    }
    
    query_string = urlencode(params)
    params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    url = urljoin(BASE_URL, PATH)
    r = requests.delete(url, headers=headers, params=params)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())

def main():
    getList()
    getDepth()
    getOrderBook()
    #con = sqlConnection()
    #createCandleTable(con,"BTCUSDT","5m")   
    refreshDataCandle()
    #con = sqlConnection()
    #createTradeTable(con,"BTCUSDT")
    refreshData()
    #createOrder('SELL','8300','0.1')
    #uuid=333105
    #cancelOrder(uuid)


    #c.execute("DROP TABLE Binance_BTCUSDT_5m")


       
