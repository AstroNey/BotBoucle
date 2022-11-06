# -- Condition to open Market LONG --
def openLongCondition(row, previousRow):
    if (row['EMA1'] > row['EMA2']
    and row['EMA2'] > row['EMA3']
    and row['EMA3'] > row['EMA4']

    and row['STOCH_RSI'] < 0.8):
        return True
    else:
        return False

# -- Condition to close Market LONG --
def closeLongCondition(row, previousRow):
    if (row['EMA3'] > row['EMA1']):
        return True
    else:
        return False

# -- Condition to open Market SHORT --
def openShortCondition(row, previousRow):
    if ( row['EMA1'] < row['EMA2']
    and row['EMA2'] < row['EMA3']
    and  row['EMA3'] < row['EMA4']

    and row['STOCH_RSI'] > 0.2 ):
        return True
    else:
        return False

# -- Condition to close Market SHORT --
def closeShortCondition(row, previousRow):
    if (row['EMA1'] > row['EMA3']):
        return True
    else:
        return False
