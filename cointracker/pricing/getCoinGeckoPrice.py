# %%
import requests
import json
import os
import time


def getCoinGeckoPrice(asset, date):
    # takes the asset ticker (ex:BTC) and date (datetime) and returns the open price
    '''
    filepath = 'unknown'
    rootDir = '.'
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        # print('Found directory: %s' % dirName)
        for fname in fileList:
            # print('\t%s' % fname)
            if fname == 'CoinGeckoIDs.json':
                filepath = dirName + '\\' + fname
    '''
    date_string = date.strftime("%d-%m-%Y")	 # format date

    try:
        # with open(filepath, 'r') as fr:  # import saved ID dictionary
        with open('../data/CoinGeckoIDs.json', 'r') as fr:  # import saved ID dictionary
            idDict = json.load(fr)

        ID = idDict[asset.lower()]
    except Exception:
        print('Error, couldn\'t find CoinGeckoIDs.json in')
        SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
        print(SCRIPTDIR, '\\data')
        price = 0

    url = "https://api.coingecko.com/api/v3/coins/"+ID+"/history?date="+date_string
    try:
        gecko = requests.get(url)
        if gecko.status_code == 429:  # if too many requests error sent
            print('Too many CoinGecko requests...waiting 90s for timeout')
            time.sleep(91)
            gecko = requests.get(url)
        price = gecko.json()['market_data']['current_price']['usd']
    except Exception:
        print('Bad CoinGecko request URL')
        print(url)
        print(gecko.status_code)
        price = 0

    return price


def updateCoinGeckoIDs():
    # query's the CoinGecko API to generate a ticker:ID dictionary
    coinList = requests.get('https://api.coingecko.com/api/v3/coins/list').json()
    '''
    filepath = 'unknown'
    rootDir = '.'
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        # print('Found directory: %s' % dirName)
        for fname in fileList:
            # print('\t%s' % fname)
            if fname == 'CoinGeckoIDs.json':
                filepath = dirName + '\\' + fname
    '''
    idDict = {}
    for coin in coinList:
        idDict[coin['symbol'].lower()] = coin['id']

    # save dictionary locally
    # with open(filepath, 'w+') as fw:
    with open('../data/CoinGeckoIDs.json', 'w+') as fw:
        json.dump(idDict, fw, indent=4)
    return


if (__name__ == '__main__'):
    updateCoinGeckoIDs()

updateCoinGeckoIDs()
'''
from datetime import datetime
start_d = datetime(2019, 8, 7)
amount = getCoinGeckoPrice('ADA', start_d)
print(amount)
'''

# %%
