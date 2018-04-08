import sys
import ConfigParser
import pandas_datareader.data as web
import os
import io
import pandas as pd
import numpy as np
import datetime as dt
import requests
import pickle
import bs4 as bs
import good_morning as gm
import request

def create_directories():
    empty_directories = np.array(["output",
                                  "data",
                                  "data/tickers",
                                  "data/prices", "data/prices/nyse", "data/prices/jse",
                                  "data/key_ratios", "data/key_ratios/nyse", "data/key_ratios/jse"])
    for i in empty_directories:
        if not os.path.exists(i):
            os.makedirs(i)
    pass

def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)

    tickers = pd.DataFrame(tickers)
    with open("./data/sp500tickers.pkl","wb") as f:
        pickle.dump(tickers,f)
    return tickers

def save_tickers(URL = 'https://en.wikipedia.org/wiki/List_of_companies_traded_on_the_JSE', exchange = 'JSE'):
    resp = requests.get(URL)
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    with open("./data/tickers/tickers_{}.pkl".format(exchange),"wb") as f:
        pickle.dump(table,f)

    return table


def load_tickers(reload = False):
    if reload:
        sp500 = save_sp500_tickers()
        nasdaq = save_nasdaq()
    else:
        sp500 = pd.read_pickle("./data/sp500tickers.pkl")
        nasdaq = pd.read_pickle("./data/nasdaq_symbols.pkl")
    return sp500, nasdaq

def save_nasdaq():
    nasdaq = web.get_nasdaq_symbols()
    nasdaq.to_pickle("./data/nasdaq_symbols.pkl")
    return nasdaq

def get_price_history(tickerset = pd.DataFrame(), ignoreset = np.array([]), replace = False, exchange = 'nyse'):
    if len(tickerset) == 0:
        sp500, nasdaq = load_tickers()
        tickers = sp500
    else:
        tickers = tickerset

    start = dt.datetime(2010,1,1)
    end = dt.datetime.now()

    for index, row in tickers.iterrows():
        ticker =  str(row[0])
        if ticker in ignoreset:
            continue
        if not os.path.exists('./data/prices/{ex}/{t}.pkl'.format(ex = exchange, t = ticker)) or replace == True:
            print('Downloading price history of {}'.format(ticker))
            df = web.DataReader(ticker, 'morningstar',start, end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            df = df.drop("Symbol", axis=1)
            df.to_pickle('./data/prices/{ex}/{t}.pkl'.format(ex = exchange, t = ticker))
        else:
            print('Already have price history for {}'.format(ticker))
    pass

def get_key_ratios(tickerset = pd.DataFrame(), ignoreset = np.array([]), replace = False, exchange = 'nyse', reg = 'usa', cur = 'USD'):
    if len(tickerset) == 0:
        sp500, nasdaq = load_tickers()
        tickers = sp500
    else:
        tickers = tickerset

    KRD = gm.KeyRatiosDownloader()


    for index, row in tickers.iterrows():
        ticker =  str(row[0])
        if ticker in ignoreset:
            continue
        if not os.path.exists('./data/key_ratios/{ex}/{t}.pkl'.format(ex = exchange, t=ticker)) or replace == True:
            print('Downloading KR of {}'.format(ticker))
            df = KRD.download(ticker, region=reg, currency=cur)
            with open('./data/key_ratios/{ex}/{t}.pkl'.format(ex = exchange, t=ticker), 'wb') as filehandle:
                #print(filehandle)
                pickle.dump(df, filehandle)
        else:
            print('Already have KR for {}'.format(ticker))

    pass

def create_price_history_table(tickers):
    PH = pd.DataFrame()
    for i in range(0,len(tickers)):
        print tickers[i]
    return PH

start = dt.datetime(2017,2,1)
end = dt.datetime.now()
df = web.get_data_morningstar('XJSE:FSR', start, end, incl_dividends = True, incl_volume = True, incl_splits = True)
df['100ma'] = df['Close'].rolling(window=100, min_periods=0).mean()
print(df.head(1000))


def main():
    """main entry poin t for script"""
    create_directories()
    ignore = np.array(['ANDV', 'BKNG', 'BHF', 'CBRE', 'DWDP', 'DXC','TPR','UAA','WELL'])
    #get_price_history(ignoreset = ignore)
    #get_key_ratios(ignoreset=ignore)
    pass


if __name__ == '__main__':
    sys.exit(main())

