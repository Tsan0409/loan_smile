from django.conf import settings

from math import floor, ceil
import pandas as pd
import datetime
import os


# カンマで区切る
def com(i):
    i = '{:,}'.format(i)
    return i


# 100万円あたりの返済額
def per_million(interest_rate, year):
    repaid = cal_paid(1000000, interest_rate, year)
    return int(repaid)


# 支払い
def cal_paid(borrowed, interest_rate, year):
    n = borrowed
    i = interest_rate / 12 / 100
    t = year * 12
    repaid = n * i * ((1 + i) ** t) / (((1 + i) ** t) - 1)
    repaid = floor(repaid)
    return int(repaid)


# 借入可能額
def borrowable(income, repayment_ratio, debt, per_million):
    n = floor((income * 10000 * repayment_ratio / 100 / 12 - debt) / per_million * 1000000)
    return n


# 必要な年収
def required_income(repayment_ratio, per_million, borrowed):
    b = borrowed * 10000
    n = ceil(b / 1000000 * per_million * 12 / repayment_ratio * 100)
    return n


# 利息の総支払額
def cal_interest(borrowed, total_repaid):
    t = int(total_repaid)
    n = int(t - borrowed)
    return n


# 月々の支払い(元金均等返済)
def P_paid(borrow, interest_rate, year):
    df = {}
    interest_month = interest_rate / 12 / 100
    times = year * 12
    pa = cal_paid(borrow, interest_rate, year)
    for n in range(times):
        interest_paid = floor(borrow * interest_month)
        principal = pa - interest_paid
        borrow -= principal
        if borrow < 0:
            pa += borrow
            principal += borrow
            borrow = 0
        df[f'{n + 1}'] = [pa, interest_paid, principal, borrow]
    return df


# 月々の再払い(元利均等返済)
def PI_paid(borrow, interest_rate, year):
    df = {}
    times = year * 12
    principal = floor(borrow / times)
    interest_month = interest_rate / 12 / 100
    for n in range(times):
        interest_paid = floor(borrow * interest_month)
        pay = interest_paid + principal
        borrow -= principal
        if n == 419:
            pay += borrow
            principal += borrow
            borrow = 0
        df[f'{n + 1}'] = [pay, interest_paid, principal, borrow]
    return df


def csv_pdata_path():
    dt = str(datetime.datetime.now())
    file_path = settings.PDATA_PATH + 'p_data_' + dt + '.csv'
    os.makedirs(settings.PDATA_PATH, exist_ok=True)

    files = os.listdir(settings.PDATA_PATH)
    if len(files) >= settings.NUM_SAVED_PDATA:
        files.sort()
        os.remove(settings.PDATA_PATH + files[0])

    return file_path


def csv_pidata_path():
    dt = str(datetime.datetime.now())
    file_path = settings.PIDATA_PATH + 'pi_data_' + dt + '.csv'
    os.makedirs(settings.PIDATA_PATH, exist_ok=True)

    files = os.listdir(settings.PIDATA_PATH)
    if len(files) >= settings.NUM_SAVED_PIDATA:
        files.sort()
        os.remove(settings.PIDATA_PATH + files[0])

    return file_path


# CSV作成(元利均等返済)
def create_PIcsv(borrow, interest, year, csv_path):
    paid = PI_paid(borrow, interest, year)
    month = []
    interest_list = []
    principal_list = []
    total_list = []
    for key, value in paid.items():
        month.append(key)
        total_list.append(value[0])
        interest_list.append(value[1])
        principal_list.append(value[2])
    js = [month, interest_list, principal_list, total_list]
    df = pd.DataFrame(paid)
    df.to_csv(csv_path)
    return js


# CSV作成(元金均等返済)
def create_Pcsv(borrow, interest, year, csv_path):
    paid = P_paid(borrow, interest, year)
    month = []
    interest_list = []
    principal_list = []
    total_list = []
    for key, value in paid.items():
        month.append(key)
        total_list.append(value[0])
        interest_list.append(value[1])
        principal_list.append(value[2])
    js = [month, interest_list, principal_list, total_list]
    df = pd.DataFrame(paid)
    df.to_csv(csv_path)
    return js


# 返済総額(元金均等返済)
def total_repaid(repaid, year):
    TotalRepaid = repaid * year * 12
    return TotalRepaid


# 返済総額(元利均等返済)
def total_PIrepaid(interest_rate, borrowed, year):
    times = year * 12
    principal = floor(borrowed / times)
    interest_m = interest_rate / 12 / 100
    total = borrowed
    for n in range(times):
        interest = floor(borrowed * interest_m)
        total += interest
        borrowed -= principal
    return int(total)


# 銀行のデータを任意の辞書型に変更
def create_bank_dict(json_encode):
    bank_info = []
    for i in json_encode:
        bank_data = {
            "bank_id": i.bank_id_id, "変動金利型": i.floating,
            "固定金利選択型01年": i.fixed_1, "固定金利選択型02年": i.fixed_2,
            "固定金利選択型03年": i.fixed_3,
            "固定金利選択型05年": i.fixed_5, "固定金利選択型07年": i.fixed_7,
            "固定金利選択型10年": i.fixed_10,
            "固定金利選択型15年": i.fixed_15, "固定金利選択型20年": i.fixed_20,
            "固定金利選択型30年": i.fixed_30,
            '全期間固定金利型11〜15年': i.fix_10to15, '全期間固定金利型16〜20年': i.fix_15to20,
            '全期間固定金利型21〜25年': i.fix_20to25, '全期間固定金利型26〜30年': i.fix_25to30,
            '全期間固定金利型31〜35年': i.fix_30to35
        }
        bank_info.append(bank_data)
    return bank_info


def create_option_dict(json_encode):
    bank_option = []
    for i in json_encode:
        bank_data = {
            "bank_id": i.bank_id_id, 'option_name': i.option_name,
            'option_rate': i.option_rate, 'option_id': i.option_id
        }
        bank_option.append(bank_data)
    return bank_option
