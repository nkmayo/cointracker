import pandas as pd
import numpy as np
import datetime
from dateutil import parser
from cointracker.pricing.getAssetPrice import getAssetPrice
from cointracker.util.util import identifyAssets


def parseOrderBook(filename, sheet):
    xl_file = pd.ExcelFile(filename)

    df = xl_file.parse(sheet)

    # change all dates into timezone-aware datetime objects to be able to compare
    # NOTE: As (regular) Coinbase doesn't provide accurate timestamps, we have to
    # hope that things work assuming it's 12AM
    for index, _ in df.iterrows():
        dateObject = df.loc[index, 'Date(UTC)']
        if not isinstance(dateObject, datetime.datetime):
            dateObject = parser.parse(dateObject)  # parse the date to datetime

        df.loc[index, 'Date(UTC)'] = \
            dateObject.replace(tzinfo=datetime.timezone.utc)  # convert to non-naive UTC

        orderType = df.loc[index, 'Type']
        orderType = orderType.upper()

    print('Order book loaded...dates converted to UTC')

    # Lets clean up the order book by combining small orders that occurred at
    # the same time and averaging their cost
    partialOrderNum = 1
    avg1USDspot = np.nan
    avg2USDspot = np.nan
    feeUSDspot = np.nan

    for index, _ in df.iterrows():
        # possible matches are orders occurring on the same day
        potMergersMask = (df['Date(UTC)'].apply(lambda x: x.strftime('%Y/%m/%d'))
                          == df.loc[index, 'Date(UTC)'].strftime('%Y/%m/%d')) & \
                         (df['Market'] == df.loc[index, 'Market']) & \
                         (df['Type'] == df.loc[index, 'Type']) & \
                         (df['Fee Coin'] == df.loc[index, 'Fee Coin'])
        tempMergers = df[potMergersMask]
        numPartialOrders = len(tempMergers)
        if numPartialOrders > 1:  # nothing to merge if there's only one in the list
            if partialOrderNum == 1:
                # total = price*amount - fee*fee spot price?
                netAmount = tempMergers['Amount'].sum()
                # total = tempMergers['Total'].sum()
                total = (tempMergers['Price']*tempMergers['Amount']).sum()  # may have been empty
                netFee = tempMergers['Fee'].sum()
                avgPrice = total/netAmount
                # weight the avg price by the amounts
                weights = tempMergers['Amount'] / tempMergers['Amount'].sum(min_count=1)
                avg1USDspot = (tempMergers['Market 1 USD Spot Price']*weights).sum(min_count=1)
                avg2USDspot = (tempMergers['Market 2 USD Spot Price']*weights).sum(min_count=1)
                feeUSDspot = (tempMergers['Fee Coin USD Spot Price']*weights).sum(min_count=1)

            # set average values
            df.loc[index, 'Price'] = avgPrice
            df.loc[index, 'Amount'] = netAmount
            # later becomes redundant... df.loc[index, 'Total'] = total
            df.loc[index, 'Fee'] = netFee
            df.loc[index, 'Market 1 USD Spot Price'] = avg1USDspot
            df.loc[index, 'Market 2 USD Spot Price'] = avg2USDspot
            df.loc[index, 'Fee Coin USD Spot Price'] = feeUSDspot

            # duplicate to the other rows in tempMergers
            df[potMergersMask] = df.loc[index, :]

            # skip the next order indicies
            if partialOrderNum < numPartialOrders:
                partialOrderNum = partialOrderNum+1
            else:
                partialOrderNum = 1
                avg1USDspot = np.nan
                avg2USDspot = np.nan
                feeUSDspot = np.nan

    # all partial orders are now duplicates, so drop them
    df = df.drop_duplicates()
    df = df.sort_values(by=['Date(UTC)'])
    df = df.reset_index(drop=True)

    # total, defined per Binance (not CB) doesn't include fees
    df['Total'] = df['Price']*df['Amount']  # may have been empty

    # reset dataframe indices after sorting by date
    df = df.sort_values(by=['Date(UTC)']).reset_index(drop=True)

    print('Orders consolidated')

    # Get missing spot prices
    dfmissing = df[df.isnull().values].drop_duplicates()  # duplicates if multiple missing per row

    # print(dfmissing)

    for index, _ in dfmissing.iterrows():
        [asset1, _, asset2, _, _] = identifyAssets(dfmissing.loc[index:index])
        date = dfmissing.loc[index, 'Date(UTC)']
        # replace each missing value in the row
        if np.isnan(dfmissing.loc[index, 'Market 1 USD Spot Price']):
            df.loc[index, 'Market 1 USD Spot Price'] = \
                getAssetPrice(asset1, date)  # df has same indicies
        if np.isnan(dfmissing.loc[index, 'Market 2 USD Spot Price']):
            df.loc[index, 'Market 2 USD Spot Price'] = \
                getAssetPrice(asset2, date)
        if np.isnan(dfmissing.loc[index, 'Fee Coin USD Spot Price']):
            df.loc[index, 'Fee Coin USD Spot Price'] = \
                getAssetPrice(dfmissing.loc[index, 'Fee Coin'], date)
    print('Prices updated')

    return df