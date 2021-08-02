# %% 
# make sure you are in the correct directory . and not ./cointracker
from cointracker.util.util import getEmptyPurchasePool, getEmptySalePool, executeOrder, prettyPrintPools
import pandas as pd
import datetime
# import ctypes  # For popup windows
import tkinter as tk
from tkinter import filedialog
from cointracker.util import orderBook as ob

# %%
if (__name__ == '__main__'):
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(title="Select current year's order book",
        filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))
    # orderbook file name
    outputPath = '../data/' # this used to work with './data', new file path?
    # sheetname = '2021 OrderBook'
    oBook = pd.read_csv(filename, parse_dates=['Date(UTC)'])
    
    startDate = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    # endDate = datetime.datetime.now()
    endDate = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
    '''
    oBook = ob.parseOrderBook(filename, sheetname)
    outputFilename = outputPath + 'OrderBookRefined.csv'
    oBook.to_csv(outputFilename, index=False, encoding='utf-8')
    '''
    # only consider orders throughout the outlined dates
    oBook = oBook[(oBook['Date(UTC)'] >= startDate) &
                  (oBook['Date(UTC)'] < endDate)]
    
    # load existing purchase pools
    purchasePath = filedialog.askopenfilename(title="Select file of existing purchase pools",
        filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))

    try:
        purchasePools = pd.read_csv(purchasePath, parse_dates=['Purchase Date'])
        # purchasePools['Purchase Date'] = \  # already done with parse_dates
        #    pd.to_datetime(purchasePools['Purchase Date'], utc=True)  # convert to datetime
        purchasePools['Holding Period Modifier'] = \
            pd.to_timedelta(purchasePools['Holding Period Modifier'])  # convert to timedelta
        # print(purchasePools.dtypes)
        # print(type(purchasePools.loc[1,'Asset']))
    except Exception:
        print("No purchase pool file read")
        purchasePools = getEmptyPurchasePool()

    # load existing sale pools (to check for wash sales near previous year end boundary)
    salePath = filedialog.askopenfilename(title="Select file of existing sale pools",
                                          filetypes=(("CSV files", "*.csv"),
                                          ("all files", "*.*")))

    try:
        salePools = pd.read_csv(salePath, parse_dates=['Purchase Date', 'Sale Date'])
        # salePools['Purchase Date'] = \
        #    pd.to_datetime(salePools['Purchase Date'], utc=True)  # convert to datetime
        # salePools['Sale Date'] = \
        #    pd.to_datetime(salePools['Sale Date'], utc=True)  # convert to datetime
        salePools['Holding Period'] = \
            pd.to_timedelta(salePools['Holding Period'])  # convert to timedelta
    except Exception:
        print("No sale pool file read")
        salePools = getEmptySalePool()

    invMethod = 'LIFO'

    # print(salePools['Long'])
    # print(list(salePools.columns.values))

    orderNum = 0

    for index, row in oBook.iterrows():
        order = oBook.loc[index:index]
        order = order.reset_index()

        temp = order.loc[0, 'Market']
        try:
            asset1, asset2 = temp.split('-')
        except Exception:
            asset1 = temp
            asset2 = 'USD'

        orderType = order.loc[0, 'Type']
        oderType = orderType.upper()
        orderNum = orderNum + 1

        print('Executing order #', orderNum)
        print('Order Type/Market: ', orderType, '/', asset1, '-', asset2)

        purchasePools, salePools = executeOrder(order, purchasePools, salePools, invMethod)

    # organize the pools as necessary
    purchasePools = purchasePools.sort_values(by=['Asset', 'Purchase Date'],
                                              ascending=[True, False])
    salePools = salePools.sort_values(by=['Asset Sold', 'Sale Date', 'Purchase Date'],
                                      ascending=[True, True, False])

    print('Finished')

    # ----------------------PRINT OUTPUT TO FILES----------------------#

    # go back through and set dates to simple MM/DD/YY (as is wanted on taxes)
    # NOTE: #x is MM/DD/YY in local time
    # NOTE: organize by date first, otherwise it will sort by month not actual date

    # salePools = purchasePools[(purchasePools['Purchase Date']>cutoffDate)
    # & (purchasePools['Asset']==asset)]
    # assetPools = potentialPools.sort_values(by=['Purchase Date'], ascending = True)

    yearSalePools = salePools[(salePools['Sale Date'] >= startDate) &
                              (salePools['Sale Date'] < endDate)]
    shortPools = yearSalePools[~yearSalePools['Long']]
    longPools = yearSalePools[yearSalePools['Long']]
    assetPools = purchasePools[purchasePools['Active']]

    # output to files
    outputFilename = outputPath + 'Puchase Pools.csv'

    purchasePools.to_csv(outputFilename, index=False, encoding='utf-8')

    outputFilename = outputPath + 'Sale Pools.csv'
    salePools.to_csv(outputFilename, index=False, encoding='utf-8')

    outputFilename = outputPath + 'Asset Pools.csv'
    assetPools.to_csv(outputFilename, index=False, encoding='utf-8')

    outputFilename = outputPath + 'Short Pools.csv'
    prettyPrintPools(shortPools, outputFilename)

    outputFilename = outputPath + 'Long Pools.csv'
    prettyPrintPools(longPools, outputFilename)

# %%
df =  pd.DataFrame({'one': [5, 6, 7 , 8]})
print(df)
# %%
df.to_csv('../data/testdf.csv')
# %%
