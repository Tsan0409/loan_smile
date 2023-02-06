from django.core.management.base import BaseCommand
from django.conf import settings
from loan_app.models import Bank, InterestRate
from loan_smile.settings_common import DRIVER

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import datetime
import os
import csv


# htmlを取り出す
def source(url):
    load_url = url
    html = requests.get(load_url)
    time.sleep(3)
    soup = BeautifulSoup(html.content, "html.parser",
                         from_encoding='utf-8')
    return soup


# 数値以外を取り除く
def arrange(soup, tag, lst):
    for element in soup.find_all(tag):
        s = element.text
        s = s.replace('年', '')
        s = s.replace(' ', '')
        s = s.replace('%', '')
        s = s.replace('％', '')
        s = s.replace('\n', '')
        s = s.replace(u'\xa0', '')
        lst.append(s)
    return lst


# 銀行データの型枠
def bank_dict(di, bank_name):
    b_dict = {'bank_name': f'{bank_name}', 'floating': 0, 'fixed_1': 0,
              'fixed_2': 0,
              'fixed_3': 0, 'fixed_5': 0,
              'fixed_7': 0, 'fixed_10': 0, 'fixed_15': 0, 'fixed_20': 0,
              'fixed_30': 0, 'fix_10to15': 0, 'fix_15to20': 0,
              'fix_20to25': 0,
              'fix_25to30': 0, 'fix_30to35': 0
              }
    for i in di:
        b_dict[i] = di[i]
    b_list = [b_dict[i] for i in b_dict]
    return b_list


# 銀行データの保存
def save_interest(di, bank_id):
    b_dict = {'bank_id': bank_id, 'floating': 0, 'fixed_1': 0,
              'fixed_2': 0,
              'fixed_3': 0, 'fixed_5': 0,
              'fixed_7': 0, 'fixed_10': 0, 'fixed_15': 0, 'fixed_20': 0,
              'fixed_30': 0, 'fix_10to15': 0, 'fix_15to20': 0,
              'fix_20to25': 0,
              'fix_25to30': 0, 'fix_30to35': 0
              }
    for i in di:
        b_dict[i] = float(di[i])
    b_list = [b_dict[i] for i in b_dict]
    interest = InterestRate(bank_id=bank_id,
                            floating=b_dict['floating'],
                            fixed_1=b_dict['fixed_1'],
                            fixed_2=b_dict['fixed_2'],
                            fixed_3=b_dict['fixed_3'],
                            fixed_5=b_dict['fixed_5'],
                            fixed_7=b_dict['fixed_7'],
                            fixed_10=b_dict['fixed_10'],
                            fixed_15=b_dict['fixed_15'],
                            fixed_20=b_dict['fixed_20'],
                            fixed_30=b_dict['fixed_30'],
                            fix_10to15=b_dict['fix_10to15'],
                            fix_15to20=b_dict['fix_15to20'],
                            fix_20to25=b_dict['fix_20to25'],
                            fix_25to30=b_dict['fix_25to30'],
                            fix_30to35=b_dict['fix_30to35'])
    print(interest)
    interest.save()
    return b_list


# 三井住友銀行
def Sumitomo_scraping():
    opt = webdriver.ChromeOptions()
    opt.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=DRIVER, options=opt)
    driver.implicitly_wait(10)
    driver.get('https://www.smbc.co.jp/kojin/jutaku_loan/kinri/')
    time.sleep(3)
    html = driver.page_source.encode('utf_8')
    time.sleep(3)
    soup = BeautifulSoup(html, 'html.parser')
    s = []
    arrange(soup, 'td', s)
    r = [(i.split('～')[0]) for i in s]
    r[18:] = []
    r = r[1::2]
    del r[1]
    r.append(r[-1])
    r.append(r[-1])
    data_name = ['floating', 'fixed_2', 'fixed_3', 'fixed_5',
                 'fixed_10', 'fix_10to15', 'fix_15to20',
                 'fix_20to25', 'fix_25to30', 'fix_30to35']
    data_dict = dict(zip(data_name, r))
    bank_id = Bank.objects.get(bank_id=1)
    save_interest(data_dict, bank_id)
    print('保存完了', data_dict)
    return bank_id


# 三菱UFJ銀行
def UFJ_scraping():
    opt = webdriver.ChromeOptions()
    opt.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=DRIVER, options=opt)
    driver.implicitly_wait(10)
    driver.get(
        'https://www.bk.mufg.jp/kariru/jutaku/yuuguu/index.html')
    time.sleep(3)
    html = driver.page_source.encode('utf_8')
    time.sleep(3)
    soup = BeautifulSoup(html, 'html.parser')
    s = []
    arrange(soup, 'strong', s)
    r = [i for i in s]
    r = r[23:33]
    s = [1, 1, 4]
    for i in s:
        r.pop(i)
    data_name = ['floating', 'fixed_3', 'fixed_20', 'fix_20to25',
                 'fix_25to30', 'fix_30to35']
    data_dict = dict(zip(data_name, r))
    bank_dict(data_dict, '三菱UFJ銀行')
    bank_id = Bank.objects.get(bank_id=2)
    save_interest(data_dict, bank_id)
    print('保存完了', data_dict)
    return bank_id


# りそな銀行
def Risona_interest():
    i = []
    soup = source('https://www.resonabank.co.jp/kojin/loan_viewer.html')
    time.sleep(3)
    arrange(soup, 'td', i)
    fix = i[225:229]
    i = i[1:40]
    new_i = []
    for index, value in enumerate(i):
        if index % 5 == 2 or index == 2:
            new_i.append(value)
    for i in fix:
        new_i.append(i)
    new_i.insert(9, new_i[8])
    new_i.insert(-1, new_i[-1])
    data_name = ['floating', 'fixed_2', 'fixed_3', 'fixed_5', 'fixed_7',
                 'fixed_10', 'fixed_15', 'fixed_20', 'fix_10to15',
                 'fix_15to20',
                 'fix_20to25', 'fix_25to30', 'fix_30to35', ]
    data_dict = dict(zip(data_name, new_i))
    bank_id = Bank.objects.get(bank_id=3)
    save_interest(data_dict, bank_id)
    print('保存完了', data_dict)
    return bank_id


# みずほ銀行
def Mizuho_scraping():
    opt = webdriver.ChromeOptions()
    opt.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=DRIVER, options=opt)
    driver.implicitly_wait(10)
    driver.get(
        'https://www.mizuhobank.co.jp/retail/products/loan/housing/housingloancost/index.html')
    time.sleep(3)
    html = driver.page_source.encode('utf_8')
    time.sleep(3)
    soup = BeautifulSoup(html, 'html.parser')
    s = []
    arrange(soup, 'td', s)
    r = [(i.split('～')[0]) for i in s]
    r[26:] = []
    r = r[1::2]
    data_name = ['floating', 'fixed_2', 'fixed_3', 'fixed_5', 'fixed_7',
                 'fixed_10', 'fixed_15', 'fixed_20', 'fix_10to15',
                 'fix_15to20',
                 'fix_20to25', 'fix_25to30', 'fix_30to35']
    data_dict = dict(zip(data_name, r))
    bank_id = Bank.objects.get(bank_id=4)
    save_interest(data_dict, bank_id)
    print('保存完了', data_dict)
    return bank_id


# 金利更新のコマンド
class Command(BaseCommand):
    help = "Update Interest Rate"

    def handle(self, *args, **options):

        date = datetime.date.today().strftime("%Y%m%d")
        file_path = settings.UPDATE_PATH + 'interest_rate_' + date + '.csv'

        os.makedirs(settings.UPDATE_PATH, exist_ok=True)

        # 銀行データのセーブ
        Sumitomo_rate = Sumitomo_scraping()
        UFJ_rate = UFJ_scraping()
        Risona_rate = Risona_interest()
        Mizuho_rate = Mizuho_scraping()

        banks = [Sumitomo_rate, UFJ_rate, Risona_rate, Mizuho_rate]

        with open(file_path, 'w') as file:
            writer = csv.writer(file)

            interest_header = [field.name for field in InterestRate._meta.fields]
            writer.writerow(interest_header)

            interests = InterestRate.objects.all().filter(bank_id_id__in=banks)
            print(interests)

            for interest in interests:
                writer.writerow([
                                str(interest.pk),
                                str(interest.floating),
                                str(interest.fixed_1),
                                str(interest.fixed_2),
                                str(interest.fixed_3),
                                str(interest.fixed_5),
                                str(interest.fixed_7),
                                str(interest.fixed_10),
                                str(interest.fixed_15),
                                str(interest.fixed_20),
                                str(interest.fixed_30),
                                str(interest.fix_10to15),
                                str(interest.fix_15to20),
                                str(interest.fix_20to25),
                                str(interest.fix_25to30),
                                str(interest.fix_30to35),
                                str(interest.updated_at)])

        # 保存ディレクトリのファイルリストを取得
        files = os.listdir(settings.UPDATE_PATH)
        if len(files) >= settings.NUM_UPDATE_INTEREST:
            files.sort()
            os.remove(settings.UPDATE_PATH + files[0])

        print('更新完了')
