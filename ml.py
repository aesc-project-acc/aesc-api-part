import pandas as pd
import json
from datetime import datetime
from time import sleep
from time import sleep
import requests
from random import choice
from sklearn.preprocessing import StandardScaler
from catboost import CatBoostClassifier, Pool
import sys
import joblib

sys.modules['sklearn.externals.joblib'] = joblib
from sklearn.externals.joblib import load

etherscan_wallets = set()

tokenview_tokens = ['yeIuqVjCtneumfMgEPle',
                    'DWa8Qccd1TV2MKguq3sQ',
                    'dF5BXo79SzRKlLxYkngT',
                    ]

model = CatBoostClassifier()
model.load_model("CatBoost.model")

dates = pd.read_csv('dates.csv')


def make_predict(addr):
    addr = addr.lower()
    result = []
    if addr in etherscan_wallets:
        # print('first return: 1')
        return 1
    for i in range(1, 51):
        try:
            print(i)
            cur = json.loads(requests.get(
                f"https://services.tokenview.io/vipapi/address/eth/{addr}/{i}/50?apikey={choice(tokenview_tokens)}").text)
            if cur["code"] == 404 or cur["code"] == '404':
                break
            result += cur['data'][0]['txs']
        except Exception as E:
            i -= 1
            print(E)
            sleep(5)
    # print(result)
    result = [(addr == el['from'].lower(), el['value'], el['time'],
               el['to'].lower() if addr == el['from'].lower() else el['from'].lower()) for el in result]
    line = result
    if (len(line) < 1):
        # print('second return: 0')
        return ((1, 0), 0)
    for i in range(len(line)):
        el = list(line[i])
        el[1] = float(el[1])
        line[i] = tuple(el)

    tnx = line
    tnx.sort(key=lambda x: x[2], reverse=True)

    number_of_tnx = len(tnx)
    is_there_2500 = number_of_tnx == 2500
    number_of_sent_tnx = sum(i[0] for i in tnx)
    number_of_received_tnx = number_of_tnx - number_of_sent_tnx
    ratio_sent_received_tnx = number_of_sent_tnx / (number_of_received_tnx + 1)

    total_sent_eth = sum(i[1] for i in tnx if i[0])
    total_received_eth = sum(i[1] for i in tnx if not i[0])
    total_eth_interacted_with = total_sent_eth + total_received_eth
    sent_received_ratio = total_sent_eth / (total_received_eth + 0.00001)

    unique_values_sent = len(set(i[1] for i in tnx if i[0]))
    unique_values_received = len(set(i[1] for i in tnx if not i[0]))
    unique_values = len(set(i[1] for i in tnx))
    ratio_unique_values_sent_received = unique_values_sent / (unique_values_received + 1)

    avg_value_of_sent_tnx = total_sent_eth / (number_of_sent_tnx + 1)
    avg_value_of_received_tnx = total_received_eth / (number_of_received_tnx + 1)
    avg_value_of_all_tnx = total_eth_interacted_with / (number_of_tnx + 1)

    time_diff_btw_first_and_last = (tnx[0][2] - tnx[-1][2])
    the_least_time_diff = min(tnx[i][2] - tnx[i + 1][2] for i in range(len(tnx) - 1)) if len(tnx) >= 2 else 0
    the_biggest_time_diff = max(tnx[i][2] - tnx[i + 1][2] for i in range(len(tnx) - 1)) if len(tnx) >= 2 else 0
    avg_sec_btw_tnx = time_diff_btw_first_and_last / number_of_tnx

    sent_times = [i[2] for i in tnx if i[0]]
    received_times = [i[2] for i in tnx if not i[0]]
    time_diff_btw_first_and_last_sent = (sent_times[0] - sent_times[-1]) if sent_times else 0
    time_diff_btw_first_and_last_received = (received_times[0] - received_times[-1]) if received_times else 0
    the_least_time_diff_sent = min([sent_times[i] - sent_times[i + 1] for i in range(len(sent_times) - 1)]) if len(
        sent_times) >= 2 else 0
    the_biggest_time_diff_sent = max([sent_times[i] - sent_times[i + 1] for i in range(len(sent_times) - 1)]) if len(
        sent_times) >= 2 else 0
    the_least_time_diff_received = min(
        [received_times[i] - received_times[i + 1] for i in range(len(received_times) - 1)]) if len(
        received_times) >= 2 else 0
    the_biggest_time_diff_received = max(
        [received_times[i] - received_times[i + 1] for i in range(len(received_times) - 1)]) if len(
        received_times) >= 2 else 0
    avg_sec_btw_tnx_sent = time_diff_btw_first_and_last_sent / (number_of_sent_tnx + 1)
    avg_sec_btw_tnx_received = time_diff_btw_first_and_last_received / (number_of_received_tnx + 1)

    unique_addresses_sent = len(set(i[-1] for i in tnx if i[0]))
    unique_addresses_received = len(set(i[-1] for i in tnx if not i[0]))
    unique_addresses_all = len(set(i[-1] for i in tnx))

    timestamp = int(tnx[0][2])
    dt_object = datetime.fromtimestamp(timestamp)

    if not dates[dates.date == str(dt_object.date())]['value'].empty:
        price_in_usd = dates[dates.date == str(dt_object.date())]['value'].iloc[0]
    else:
        price_in_usd = \
        eval(requests.get(f'https://min-api.cryptocompare.com/data/pricehistorical?fsym=ETH&tsyms=USD&ts={timestamp}').text)[
            'ETH']['USD']

    total_sent_eth_usd = total_sent_eth * price_in_usd
    total_received_eth_usd = total_received_eth * price_in_usd
    total_eth_interacted_with_usd = total_eth_interacted_with * price_in_usd
    avg_value_of_sent_tnx_usd = total_sent_eth_usd / (number_of_sent_tnx + 1)
    avg_value_of_received_tnx_usd = total_received_eth_usd / (number_of_received_tnx + 1)
    avg_value_of_all_tnx_usd = total_eth_interacted_with_usd / (number_of_tnx + 1)

    # data = pd.Series([number_of_tnx, is_there_2500, number_of_sent_tnx, number_of_received_tnx, ratio_sent_received_tnx, total_sent_eth, total_received_eth, total_eth_interacted_with, sent_received_ratio, unique_values_sent, unique_values_received, unique_values, ratio_unique_values_sent_received, avg_value_of_sent_tnx, avg_value_of_received_tnx, avg_value_of_all_tnx, time_diff_btw_first_and_last, the_least_time_diff, the_biggest_time_diff, avg_sec_btw_tnx, time_diff_btw_first_and_last_sent, time_diff_btw_first_and_last_received, the_least_time_diff_sent, the_biggest_time_diff_sent, the_least_time_diff_received, the_biggest_time_diff_received, avg_sec_btw_tnx_sent, avg_sec_btw_tnx_received, unique_addresses_sent, unique_addresses_received, unique_addresses_all, total_sent_eth_usd, total_received_eth_usd, total_eth_interacted_with_usd, avg_value_of_sent_tnx_usd, avg_value_of_received_tnx_usd, avg_value_of_all_tnx_usd])
    data = [number_of_tnx, number_of_sent_tnx, number_of_received_tnx, ratio_sent_received_tnx, total_sent_eth,
            total_received_eth, total_eth_interacted_with, sent_received_ratio, unique_values_sent,
            unique_values_received, unique_values, ratio_unique_values_sent_received, avg_value_of_sent_tnx,
            avg_value_of_received_tnx, avg_value_of_all_tnx, time_diff_btw_first_and_last, the_least_time_diff,
            the_biggest_time_diff, avg_sec_btw_tnx, time_diff_btw_first_and_last_sent,
            time_diff_btw_first_and_last_received, the_least_time_diff_sent, the_biggest_time_diff_sent,
            the_least_time_diff_received, the_biggest_time_diff_received, avg_sec_btw_tnx_sent,
            avg_sec_btw_tnx_received, unique_addresses_sent, unique_addresses_received, unique_addresses_all,
            total_sent_eth_usd, total_received_eth_usd, total_eth_interacted_with_usd, avg_value_of_sent_tnx_usd,
            avg_value_of_received_tnx_usd, avg_value_of_all_tnx_usd]
    print(len(data))
    t = time = time_diff_btw_first_and_last

    data += [number_of_tnx / t, number_of_sent_tnx / t, number_of_received_tnx / t, total_sent_eth / t,
             total_received_eth / t, total_eth_interacted_with / t, unique_values_sent / t, unique_values_received / t,
             unique_values / t, unique_addresses_sent / t, unique_addresses_received / t,
             unique_addresses_all / t, total_sent_eth_usd / t, total_received_eth_usd / t,
             total_eth_interacted_with_usd / t]
    print(len(data))
    scaler = load("std_scaler_on_divided_by_time.bin")
    scaled = scaler.transform([pd.Series(data)])

    to_model = list(scaled[0]) + [is_there_2500]

    p, t = model.predict_proba(to_model), model.predict(to_model)

    return f"Кошелек задействован в отмывании денежных средств с вероятностью {int(p[1]*100)}%" if t else f"Кошелек НЕ задействован в отмывании денежных средств с вероятностью {int(p[0]*100)}%"

def get_predict_by_address(address):
    return make_predict(address)


