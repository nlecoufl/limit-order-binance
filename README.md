# TD9 : Automation Trading
Made by Nicolas Matusiak an Nicolas Lecouflet

The python code is available here : 

--> [Python](https://github.com/nlecoufl/TD9_Monnaie_Numerique/blob/master/TD09.py)
### API Keys
Replace API_KEY and SECRET_KEY with your own keys

    API_KEY = 'YOUR_PUBLIC_KEY'
    SECRET_KEY = 'YOUR_PRIVATE_KEY'
## Main 
You can run this main if you want to display all the functions. We commented createOrder and cancelOrder because it doesn't work (we don't have fund). 

**WARNING:** If you rerun main() a second time, the console will display that the table already exists. Just comment 'con = sqlConnection()' and 'createCandleTable(con,"BTCUSDT","5m")' and 'createTradeTable(con,"BTCUSDT")' to avoid this.

    def main():
        getList()
        getDepth()
        getOrderBook()
        con = sqlConnection()
        createCandleTable(con,"BTCUSDT","5m")   
        refreshDataCandle()
        con = sqlConnection()
        createTradeTable(con,"BTCUSDT")
        refreshData()
        #createOrder('SELL','8300','0.1')
        #uuid=333105
        #cancelOrder(uuid)

## Instruction of TD
### Get a list of all available cryptocurrencies and display it

    >> getList()
Returns all the cryptocurrencies and their price.

### Create a function to display the ’ask’ or ‘bid’ price of an asset

    >> getDepth('bid','BNBEUR')
By default, the pair is "BTCUSDT" 

We created an additional function named removeKey in order to display only bid or only ask prices :

    def removeKey(d, key):
        r = dict(d)
        del r[key]
        return r
  
    
### Get order book for an asset
  
    >> getOrderBook('BNBEUR')
By default, the pair is "BTCUSDT"
    

### Create a function to read agregated trading data (candles) (Don't worry, it will display an error at the end of the console because you didn't create the sqlite table yet)
    
    >> refreshDataCandle('BTCUSDT','5m')
    
### Create a sqlite table to store said data

    con=sqlConnection()
    createCandleTable(con,'BTCUSDT','5m')
See the functions in the python file, sqlConnection handle the connection to sqlite and createCandleTable create the table and names is "Binance_BTCUSDT_5m" for this example. Then you can rerun refreshDataCandle()

### Store candle data in the db & Modify function to update when new candle data is available
We adapted the refreshDataCandle() function to add datas to the base with this command:
    
    c.executemany('INSERT INTO ' + setTableName + ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', r.json())
You just have to rerun the function to add the data to the base. If you want to clear the db each time you rerun the function, just had the following before the previous command :

    c.execute('DELETE * from ' + setTableName)
    
### Create a function to extract all available trade data
Same logic as before :

    con=sqlConnection()
    createTradeTable(con,'BTCUSDT')

### Store the data in sqlite
Had to manipulate a bit the request r before adding it in the table with the following :
        
        l=[]
        for i in range(len(r.json())):
            temp=[]
            for valeur in r.json()[i].values():
                temp.append(valeur)
            l.append(temp)

Explanation : r.json() object was like a dictionnary (i.e. : '{"a":1, "b":2, etc.}') and it was impossible to add it to the table. After this, the l object contains only the values (i.e. : '{1,2,etc.}').

### Create an order
Will display an error since we have no fund, and the price must be close to the traded price to make the order.

    >> createOrder('SELL', '8300', '0.1', 'BTCUSDT', 'LIMIT')
    
### Cancel an order
Need the uuid of the order to cancel it, which we don't have.

    >> cancelOrder(uuid, 'BTCUSDT')
