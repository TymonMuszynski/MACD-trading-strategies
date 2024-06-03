# Tymon Muszyński 193537
import pandas as pd
import matplotlib.pyplot as plt
def calcAlfa(n):
    return 2 / (n + 1)


def aflaRoot(alfa, n):
    return (1 - alfa) ** n


def calcEMAn(n, index, type):
    datetime = DataSet['datetime'].iloc[index]
    if index - n < 0:
        n = index
    n += 1
    date_range = pd.date_range(end=datetime, periods=n)
    selected_data = DataSet[DataSet['datetime'].isin(date_range)]
    EMAn_devisor = 0
    EMAn_sum = 0
    for i in range(n):
        alfa = calcAlfa(n)
        alfa_ptr = aflaRoot(alfa, i)

        EMAn_devisor += alfa_ptr
        match type:
            case "EMA12":
                EMAn_sum += alfa_ptr * selected_data['stock'].iloc[n - i - 1]
            case "EMA26":
                EMAn_sum += alfa_ptr * selected_data['stock'].iloc[n - i - 1]
            case "EMA9":
                EMAn_sum += alfa_ptr * selected_data['MACD'].iloc[n - i - 1]

    EMAn = EMAn_sum / EMAn_devisor
    match type:
        case "EMA12":
            DataSet.loc[DataSet['datetime'] == datetime, 'EMA12'] = EMAn
        case "EMA26":
            DataSet.loc[DataSet['datetime'] == datetime, 'EMA26'] = EMAn
        case "EMA9":
            DataSet.loc[DataSet['datetime'] == datetime, 'SIGNAL'] = EMAn


# Variables declaration
df = pd.read_csv("BTC-USD-short.csv")

DataSet = pd.DataFrame({
    'datetime': [],
    'stock': [],
    'EMA12': [],
    'EMA26': [],
    'SIGNAL': [],
    'MACD': [],
    'wallet': [],
    'shares': []
})

df["Date"] = pd.to_datetime(df["Date"])
DataSet['datetime'] = df['Date']
DataSet['stock'] = df['High']

DataSet = DataSet.sort_values('datetime')

shares = 1000
wallet = 0
sold = False
operation_procenatge = 1
MACD_limit = 0
# MACD_limit_range = 200
action_procenatge = 10000
stock_price = 0

# Main
calcEMAn(26, 80, "EMA26")

for i in range(len(DataSet)):
    calcEMAn(26, i, "EMA26")
    calcEMAn(12, i, "EMA12")
for i in range(len(DataSet)):
    MACDn = DataSet['EMA12'].iloc[i] - DataSet['EMA26'].iloc[i]
    DataSet.iloc[i, DataSet.columns.get_loc('MACD')] = MACDn
for i in range(len(DataSet)):
    calcEMAn(9, i, "EMA9")

# limit_history = []
# finnal_profit = []
# for limit in range(1, MACD_limit_range, 5):
shares = 1000
wallet = 0
# MACD_limit = limit
intersection_points_sell = []
intersection_points_buy = []
shares_history = [shares]
wallet_history = [wallet]
for i in range(1, len(DataSet)):
    if (DataSet['MACD'][i - 1] < DataSet['SIGNAL'][i - 1]) and (DataSet['MACD'][i] > DataSet['SIGNAL'][i]):
        intersection_points_buy.append(DataSet['datetime'][i])
        if sold and (
                DataSet['MACD'][i] - DataSet['SIGNAL'][i] > MACD_limit or DataSet['MACD'][i] - DataSet['SIGNAL'][
            i] < -MACD_limit):
            stock_price = DataSet['stock'][i]
            shares = (wallet * operation_procenatge) / stock_price + shares
            wallet -= wallet * operation_procenatge
            sold = False
            print(i, "Bitcoins: ", shares, "BTC")
            print(i, "Wallet USD: ", wallet, "$")
    if (DataSet['MACD'][i - 1] > DataSet['SIGNAL'][i - 1]) and (DataSet['MACD'][i] < DataSet['SIGNAL'][i]):
        intersection_points_sell.append(DataSet['datetime'][i])
        if not sold and (
                DataSet['MACD'][i] - DataSet['SIGNAL'][i] > MACD_limit or DataSet['MACD'][i] - DataSet['SIGNAL'][
            i] < -MACD_limit):
            stock_price = DataSet['stock'][i]
            wallet = stock_price * shares * operation_procenatge + wallet
            shares -= shares * operation_procenatge
            sold = True
            print(i, "Bitcoins: ", shares, "BTC")
            print(i, "Wallet USD: ", wallet, "$")
    shares_history.append(shares * action_procenatge)
    wallet_history.append(wallet)
print("Final Wallet Value:", wallet + stock_price * shares, "$")
# print("Limit:", limit, "Portfel: ", wallet + stock_price * shares, "$")
# limit_history.append(limit)
# finnal_profit.append(wallet + stock_price * shares)


# MACD-SIGNAL
DataSet.plot(kind='line', x='datetime', y=['MACD', 'SIGNAL'], linewidth=2)
plt.plot(intersection_points_sell, DataSet.loc[DataSet['datetime'].isin(intersection_points_sell)]['MACD'], 'ro',
         markersize=4)
plt.plot(intersection_points_buy, DataSet.loc[DataSet['datetime'].isin(intersection_points_buy)]['MACD'], 'go',
         markersize=4)
plt.xlabel('Date')
plt.ylabel('MACD - SIGNAL')
plt.title('MACD SIGNAL intersections')
plt.grid(True, which='both', linestyle='--', color='gray')
plt.savefig('MACD-SIGNAL.png', dpi=1000)
plt.show()

# Show BTC price
DataSet.plot(kind='line', x='datetime', y='stock')
plt.plot(intersection_points_sell, DataSet.loc[DataSet['datetime'].isin(intersection_points_sell)]['stock'], 'ro',
         markersize=1)
plt.plot(intersection_points_buy, DataSet.loc[DataSet['datetime'].isin(intersection_points_buy)]['stock'], 'go',
         markersize=1)
plt.xlabel('Date')
plt.ylabel('Stock USD')
plt.title('BTC USD price')
plt.grid(True, which='both', linestyle='--', color='gray')
# plt.savefig('STOCK.png', dpi=1000)
plt.show()

# Combined macd signal and BTC USD
fig, (pt1, pt2) = plt.subplots(2, 1, sharex=True)

pt1.plot(DataSet['datetime'], DataSet['MACD'], label='MACD')
pt1.plot(DataSet['datetime'], DataSet['SIGNAL'], label='SIGNAL')
pt1.plot(intersection_points_sell, DataSet.loc[DataSet['datetime'].isin(intersection_points_sell)]['MACD'], 'ro',
         markersize=4, label='Sell Signal')
pt1.plot(intersection_points_buy, DataSet.loc[DataSet['datetime'].isin(intersection_points_buy)]['MACD'], 'go',
         markersize=4, label='Buy Signal')
pt1.set_xlabel('Date')
pt1.set_ylabel('MACD - SIGNAL')
pt1.set_title('MACD SIGNAL intersections')
pt1.grid(True, which='both', linestyle='--', color='gray')

pt2.plot(DataSet['datetime'], DataSet['stock'])
pt2.plot(intersection_points_sell, DataSet.loc[DataSet['datetime'].isin(intersection_points_sell)]['stock'], 'ro',
         markersize=4)
pt2.plot(intersection_points_buy, DataSet.loc[DataSet['datetime'].isin(intersection_points_buy)]['stock'], 'go',
         markersize=4)
pt2.set_xlabel('Date')
pt2.set_ylabel('Stock USD')
pt2.set_title('BTC USD price')
pt2.grid(True, which='both', linestyle='--', color='gray')

pt1.legend()

plt.tight_layout()
# plt.savefig('Combined_Chart.png', dpi=1000)
plt.show()

# Wallet over time
DataSet['wallet'] = wallet_history
DataSet['shares'] = shares_history
DataSet.plot(kind='line', x='datetime', y=['wallet', 'shares'])
plt.xlabel('Date')
plt.ylabel('Wallet Value USD')
plt.title('Wallet Balance Over Time')
plt.grid(True, which='both', linestyle='--', color='gray')
# plt.savefig('WALLET.png', dpi=1000)
plt.show()
