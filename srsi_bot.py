from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.ticker as ticker
import notify

############## SETTINGS #################
api_key =           'past_api_key_here' # Your own Alpha Vantage api key
symbol =            'FB'                # You can use every Stock symbol here
horizontal_line =   True                # True: to display sell and buy line (20 and 80 on SRSI), False: to display none
window_length =     14                  # Window_lenght to use with SRSI
interval =          1                   # Only use 1, 5, 15, 30 or 60 (this is the chart interval in minutes)
############## SETTINGS #################





fig, axes = plt.subplots(nrows=2, ncols=1,figsize=(20,10))
fig.canvas.set_window_title(symbol)
while True:
    axes[0].cla()
    axes[1].cla() 
    ts = TimeSeries(key=api_key,output_format='pandas', indexing_type='date')   
    intermin = str(interval) + 'min'
    df = ts.get_intraday(symbol,intermin)
    df = df[0]
    close = df['4. close']
    delta = close.diff()
    delta = delta[1:] 
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up1 = up.ewm(ignore_na=False,min_periods=0,adjust=True,com=14).mean()
    roll_down1 = down.abs().ewm(ignore_na=False,min_periods=0,adjust=True,com=14).mean()
    roll_up2 = up.rolling(window=14,center=False).mean()
    roll_down2 = down.abs().rolling(window=14,center=False).mean()
    RS2 = roll_up2 / roll_down2
    df['RSI'] = 100.0 - (100.0 / (1.0 + RS2))
    df['L14'] = df['3. low'].rolling(window=14).min()
    df['H14'] = df['2. high'].rolling(window=14).max()
    df['StochRSI'] = 100*((df['4. close'] - df['L14']) / (df['H14'] - df['L14']) )
    df = df[14:]
    y = []
    c = ''
    mark = []
    below17 = False
    back_above20 = False
    cnt = 1
    above80 = False
    for val in df['StochRSI']:
        if val < 17:
            below17 = True
        if below17 and val > 20 and val <80 and not back_above20 :
            back_above20 = True
            mark.append(cnt-1)
            y.append(val)
            c = c + 'g'
            below17 = False
            if df.index[-1] == df.index[cnt-1]:
                notify.notify_log("Buy %s now! It's at $%s." %(symbol,df['4. close'][cnt-1]))
        if back_above20 and val > 80:
            mark.append(cnt-1)
            y.append(val)
            c = c + 'r'
            back_above20 = False
            below17 = False
            if df.index[-1] == df.index[cnt-1]:
                notify.notify_log("Sell %s now! It's at $%s." %(symbol,df['4. close'][cnt-1]))            
        cnt += 1
    x = [0,2,4,6,8]
    axes[1].scatter(mark,y,s=100,c=c)
    axes[0].set_title('Close')
    df.index = pd.to_datetime(df.index)
    axes[0].plot(df.index.strftime('%b %d, %H:%M'), df['4. close'],color='darkblue')
    axes[1].plot(df.index.strftime('%b %d, %H:%M'), df['RSI'],color='lightgrey')
    axes[1].plot(df.index.strftime('%b %d, %H:%M'), df['StochRSI'],color='orange')
    if horizontal_line == True:
        axes[1].axhline(y=80, color='r', linestyle='-')
        axes[1].axhline(y=20, color='g', linestyle='-')
    axes[0].set_xlabel('')
    axes[1].set_xlabel('')
    axes[1].legend(['RSI','StochRSI'])
    axes[0].legend([symbol])
    axes[0].xaxis.set_major_locator(ticker.MultipleLocator(15))
    axes[0].xaxis.set_minor_locator(ticker.MultipleLocator(1))
    axes[1].xaxis.set_major_locator(ticker.MultipleLocator(15))
    axes[1].xaxis.set_minor_locator(ticker.MultipleLocator(1))    
    axes[1].set_title('Oscillator')
    plt.tight_layout()
    axes[0].grid(b=True)
    axes[1].grid(b=True)
    sleeptime = (interval * 60) - 5
    plt.pause(sleeptime)
plt.show()

