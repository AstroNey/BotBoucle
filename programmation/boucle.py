import pandas as pd
from binance.client import Client
import ta
import fonctionOrder

def boucle():

    # -- Define Binance Client --
    client = Client()

    # -- You can change the crypto pair ,the start date and the time interval below --
    pairName = "ETHUSDT"
    startDate = "01 january 2018"
    timeInterval = Client.KLINE_INTERVAL_1HOUR

    # -- Load all price data from binance API --
    klinesT = client.get_historical_klines(pairName, timeInterval, startDate)

    # -- Define your dataset --
    df = pd.DataFrame(klinesT, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['open'] = pd.to_numeric(df['open'])

    # -- Set the date to index --
    df = df.set_index(df['timestamp'])
    df.index = pd.to_datetime(df.index, unit='ms')
    del df['timestamp']

    print("Data loaded 100%")

    # -- Drop all columns we do not need --
    df.drop(df.columns.difference(['open','high','low','close','volume']), 1, inplace=True)

    a = 1
    b = 1
    c = 1
    d = 1
    print("start")
    for a in range(1,8):
        df['EMA1'] = ta.trend.ema_indicator(close=df['close'], window=a)
        for b in range(20, 71):
            df['EMA2'] = ta.trend.ema_indicator(close=df['close'], window=b)
            for c in range(71, 130):
                df['EMA3'] = ta.trend.ema_indicator(close=df['close'], window=c)
                for d in range(200, 300):
                    df['EMA4']= ta.trend.ema_indicator(close=df['close'], window=d)
                    # -- Stochasitc RSI --
                    df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=14, smooth1=3, smooth2=3)

                    # -- Uncomment the line below if you want to check your dataset with indicators --

                    dfTest = df.copy()

                    # -- If you want to run your BackTest on a specific period, uncomment the line below --
                    # dfTest = df['2021-03-01':'2021-09-01']

                    # -- Definition of dt, that will be the dataset to do your trades analyses --
                    dt = None
                    dt = pd.DataFrame(columns=['date', 'position', 'reason', 'price', 'frais', 'wallet', 'drawBack'])

                    # -- You can change variables below --
                    leverage = 3
                    wallet = 1000
                    makerFee = 0.0002
                    takerFee = 0.0007

                    # -- Do not touch these values --
                    initalWallet = wallet
                    lastAth = wallet
                    previousRow = dfTest.iloc[0]
                    stopLoss = 0
                    takeProfit = 500000
                    orderInProgress = ''
                    longIniPrice = 0
                    shortIniPrice = 0
                    longLiquidationPrice = 500000
                    shortLiquidationPrice = 0

                    # -- Iteration on all your price dataset (df) --
                    for index, row in dfTest.iterrows():
                        # -- If there is an order in progress --
                        if orderInProgress != '':
                            # -- Check if there is a LONG order in progress --
                            if orderInProgress == 'LONG':
                                # -- Check Liquidation --
                                if row['low'] < longLiquidationPrice:
                                    print('/!\ YOUR LONG HAVE BEEN LIQUIDATED the',index)
                                    break

                                # -- Check Stop Loss --
                                elif row['low'] < stopLoss:
                                    orderInProgress = ''
                                    closePrice = stopLoss
                                    closePriceWithFee = closePrice - takerFee * closePrice
                                    pr_change = (closePriceWithFee - longIniPrice) / longIniPrice
                                    wallet = wallet + wallet*pr_change*leverage

                                    # -- Check if your wallet hit a new ATH to know the drawBack --
                                    if wallet > lastAth:
                                        lastAth = wallet

                                # -- Check If you have to close the LONG --
                                elif fonctionOrder.closeLongCondition(row, previousRow) == True:
                                    orderInProgress = ''
                                    closePrice = row['close']
                                    closePriceWithFee = row['close'] - takerFee * row['close']
                                    pr_change = (closePriceWithFee - longIniPrice) / longIniPrice
                                    wallet = wallet + wallet*pr_change*leverage

                                    # -- Check if your wallet hit a new ATH to know the drawBack --
                                    if wallet > lastAth:
                                        lastAth = wallet

                            # -- Check if there is a SHORT order in progress --
                            elif orderInProgress == 'SHORT':
                                # -- Check Liquidation --
                                if row['high'] > shortLiquidationPrice:
                                    print('/!\ YOUR SHORT HAVE BEEN LIQUIDATED the',index)
                                    break

                                # -- Check stop loss --
                                elif row['high'] > stopLoss:
                                    orderInProgress = ''
                                    closePrice = stopLoss
                                    closePriceWithFee = closePrice + takerFee * closePrice
                                    pr_change = -(closePriceWithFee - shortIniPrice) / shortIniPrice
                                    wallet = wallet + wallet*pr_change*leverage

                                    # -- Check if your wallet hit a new ATH to know the drawBack --
                                    if wallet > lastAth:
                                        lastAth = wallet

                                # -- Check If you have to close the SHORT --
                                elif fonctionOrder.closeShortCondition(row, previousRow) == True:
                                    orderInProgress = ''
                                    closePrice = row['close']
                                    closePriceWithFee = row['close'] + takerFee * row['close']
                                    pr_change = -(closePriceWithFee - shortIniPrice) / shortIniPrice
                                    wallet = wallet + wallet*pr_change*leverage

                                    # -- Check if your wallet hit a new ATH to know the drawBack --
                                    if wallet > lastAth:
                                        lastAth = wallet


                        # -- If there is NO order in progress --
                        if orderInProgress == '':
                            # -- Check If you have to open a LONG --
                            if fonctionOrder.openLongCondition(row, previousRow) == True:
                                orderInProgress = 'LONG'
                                closePrice = row['close']
                                longIniPrice = row['close'] + takerFee * row['close']
                                tokenAmount = (wallet * leverage) / row['close']
                                longLiquidationPrice = longIniPrice - (wallet/tokenAmount)
                                stopLoss = closePrice - 0.03 * closePrice

                            # -- Check If you have to open a SHORT --
                            if fonctionOrder.openShortCondition(row, previousRow) == True:
                                orderInProgress = 'SHORT'
                                closePrice = row['close']
                                shortIniPrice = row['close'] - takerFee * row['close']
                                tokenAmount = (wallet * leverage) / row['close']
                                shortLiquidationPrice = shortIniPrice + (wallet/tokenAmount)
                                stopLoss = closePrice + 0.03 * closePrice
                    if wallet >= 1500000:
                        data = (a, b, c, d, wallet)
                        with open('resultat.txt') as f:
                            f.write(data)

