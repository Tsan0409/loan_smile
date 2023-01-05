import logging

import params as params
import requests
from django.core import serializers
from django.shortcuts import render

from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse


from .forms import InquiryForm, SampleForm, BorrowAbleForm,\
    RequiredIncomeForm, RepaidForm, CreateInterestForm,\
    ChangeInterestForm, ChoiceBankForm
from .models import Bank, InterestRate, Option


from math import floor, ceil
import pandas as pd
import matplotlib.pyplot as plt



logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = 'index.html'


# サンプル(form)
class SampleView(generic.FormView, LoginRequiredMixin):

    form_class = SampleForm
    model = InterestRate
    template_name = 'sample.html'

    def form_valid(self, form):
        # バリデーション後のデータを変数にぶち込む
        ppp= {
            'a': 'Hi django',
            'b': [3, 4, 5],
        }
        data = form.cleaned_data
        print(data)
        text = data['text']
        search = data['search']
        replace = data['replace']
        new_text = text.replace(search, replace)
        ctxt = self.get_context_data(new_text=new_text, form=form, ppp=ppp)
        print(f'ctxt{ctxt}')
        return self.render_to_response(ctxt)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_name = self.get_userid()
        json_encode2 = serializers.serialize("json", InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id=user_name))
        context['Rates2'] = json_encode2
        json_encode3 = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id=user_name)
        print(json_encode3)
        bank_info = []
        for i in json_encode3:
            print(i)
            bank_data = {
                "bank_name": i.bank_id.bank_name, "変動金利型": i.floating,
                "固定金利選択型01年": i.fixed_1, "固定金利選択型02年": i.fixed_2, "固定金利選択型03年": i.fixed_3,
                "固定金利選択型05年": i.fixed_5, "固定金利選択型07年": i.fixed_7, "固定金利選択型10年": i.fixed_10,
                "固定金利選択型15年": i.fixed_15, "固定金利選択型20年": i.fixed_20, "固定金利選択型30年": i.fixed_30,
                '全期間固定金利型11〜15年': i.fix_10to15, '全期間固定金利型16〜20年': i.fix_15to20,
                '全期間固定金利型21〜25年': i.fix_20to25, '全期間固定金利型26〜30年': i.fix_25to30,
                '全期間固定金利型31〜35年': i.fix_30to35
                    }
            bank_info.append(bank_data)
        print(bank_info[0].keys())
        a = bank_info[0].values()
        print(a)
        print(bank_info)
        context['Rate3'] = bank_info
        return context

    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = '1'
        else:
            user_name = self.request.user
        return user_name

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        user_name = self.get_userid()
        print(f'view: {user_name}')
        kwgs["user"] = user_name
        return kwgs




class InquiryView(generic.FormView):
    template_name = 'inquiry.html'
    form_class = InquiryForm
    success_url = reverse_lazy('loan_app:inquiry')

    # フォームのバリデーションが問題なければ動くメソッド
    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました')
        logger.info(f'Inquiry sent by {form.cleaned_data["name"]}')
        return super().form_valid(form)


class BorrowAbleView(generic.FormView, LoginRequiredMixin):

    form_class = BorrowAbleForm
    model = InterestRate
    template_name = 'borrow_able.html'

    # 計算処理
    def form_valid(self, form):
        data = form.cleaned_data
        print(1)
        income = data['income']
        repayment_ratio = data['repayment_ratio']
        debt = data['debt']
        year = data['year']
        select = data['select']
        print(2)
        if select == '0':
            interest_rate = data['interest']
            print(3)
        else:
            print(4)
            interest_rate = float(self.request.POST['bank_rate'])
        if interest_rate == 0 or interest_rate is None:
            print(5)
            interest_rate = 0
            ctxt = self.get_context_data(interest_rate=interest_rate, form=form)
            return self.render_to_response(ctxt)
        print(6)
        million_per = self.million_per(interest_rate, year)
        borrowable = self.com(self.borrowable(income, repayment_ratio, debt, million_per))
        ctxt = self.get_context_data(interest_rate=interest_rate, borrowable=borrowable, form=form)
        print(7)
        return self.render_to_response(ctxt)

    # フォームにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_info = self.get_bank_info()
        context['BankInfo'] = bank_info
        return context

    # ログイン情報をform.pyに送る
    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        user_name = self.get_userid()
        print(f'user_id　view: {user_name}')
        kwgs["user"] = user_name
        return kwgs

    # 金利作成
    def get_bank_info(self):
        user_name = self.get_userid()
        json_encode = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id=user_name)
        bank_info = []
        for i in json_encode:
            bank_data = {
                "bank_id": i.bank_id_id, "変動金利型": i.floating,
                "固定金利選択型01年": i.fixed_1, "固定金利選択型02年": i.fixed_2, "固定金利選択型03年": i.fixed_3,
                "固定金利選択型05年": i.fixed_5, "固定金利選択型07年": i.fixed_7, "固定金利選択型10年": i.fixed_10,
                "固定金利選択型15年": i.fixed_15, "固定金利選択型20年": i.fixed_20, "固定金利選択型30年": i.fixed_30,
                '全期間固定金利型11〜15年': i.fix_10to15, '全期間固定金利型16〜20年': i.fix_15to20,
                '全期間固定金利型21〜25年': i.fix_20to25, '全期間固定金利型26〜30年': i.fix_25to30,
                '全期間固定金利型31〜35年': i.fix_30to35
                    }
            bank_info.append(bank_data)
        return bank_info

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = '1'
        else:
            user_name = self.request.user
        return user_name

    # 100万あたりの返済額
    def million_per(self, interest_rate, year):
        repaid = self.paid(100, interest_rate, year)
        return int(repaid)

    # 借入可能額
    def borrowable(self, income, repayment_ratio, debt, million_per):
        n = floor((income * 10000 * repayment_ratio / 100 / 12 - debt) / million_per * 1000000)
        return n

    # 支払い
    def paid(self, borrowed, interest_rate, year):
        n = borrowed * 10000
        i = interest_rate / 12 / 100
        t = year * 12
        repaid = n * i * ((1 + i) ** t) / (((1 + i) ** t) - 1)
        repaid = floor(repaid)
        return int(repaid)

    def com(self, i):
        i = '{:,}'.format(i)
        return i


class RequiredIncomeView(generic.FormView, LoginRequiredMixin):

    form_class = RequiredIncomeForm
    model = InterestRate
    template_name = 'required_income.html'

    # 計算処理
    def form_valid(self, form):
        print('c')
        data = form.cleaned_data
        borrow = data['borrow']
        repayment_ratio = data['repayment_ratio']
        year = data['year']
        select = data['select']
        if select == '0':
            interest_rate = data['interest']
        else:
            interest_rate = float(self.request.POST['bank_rate'])
        if interest_rate == 0 or interest_rate is None:
            interest_rate = 0
            ctxt = self.get_context_data(interest_rate=interest_rate, form=form)
            return self.render_to_response(ctxt)
        million_per = self.million_per(interest_rate, year)
        required_income = self.com(self.required_income(repayment_ratio, million_per, borrow))
        ctxt = self.get_context_data(interest_rate=interest_rate, required_income=required_income, form=form)
        return self.render_to_response(ctxt)

    # フォームにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_info = self.get_bank_info()
        context['BankInfo'] = bank_info
        return context

    # ログイン情報をform.pyに送る
    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        user_name = self.get_userid()
        kwgs["user"] = user_name
        return kwgs

    # 金利作成
    def get_bank_info(self):
        user_name = self.get_userid()
        json_encode = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id=user_name)
        bank_info = []
        for i in json_encode:
            bank_data = {
                "bank_id": i.bank_id_id, "変動金利型": i.floating,
                "固定金利選択型01年": i.fixed_1, "固定金利選択型02年": i.fixed_2, "固定金利選択型03年": i.fixed_3,
                "固定金利選択型05年": i.fixed_5, "固定金利選択型07年": i.fixed_7, "固定金利選択型10年": i.fixed_10,
                "固定金利選択型15年": i.fixed_15, "固定金利選択型20年": i.fixed_20, "固定金利選択型30年": i.fixed_30,
                '全期間固定金利型11〜15年': i.fix_10to15, '全期間固定金利型16〜20年': i.fix_15to20,
                '全期間固定金利型21〜25年': i.fix_20to25, '全期間固定金利型26〜30年': i.fix_25to30,
                '全期間固定金利型31〜35年': i.fix_30to35
                    }
            bank_info.append(bank_data)
        return bank_info

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = '1'
        else:
            user_name = self.request.user
        return user_name

    def required_income(self, repayment_ratio, million_per, borrowed):
        b = borrowed * 10000
        n = ceil(b / 1000000 * million_per * 12 / repayment_ratio * 100)
        return n

    # 100万あたりの返済額
    def million_per(self, interest_rate, year):
        repaid = self.paid(100, interest_rate, year)
        return int(repaid)

    # 支払い
    def paid(self, borrowed, interest_rate, year):
        n = borrowed * 10000
        i = interest_rate / 12 / 100
        t = year * 12
        repaid = n * i * ((1 + i) ** t) / (((1 + i) ** t) - 1)
        repaid = floor(repaid)
        return int(repaid)

    def com(self, i):
        i = '{:,}'.format(i)
        return i


class RepaidView(generic.FormView, LoginRequiredMixin):

    form_class = RepaidForm
    model = InterestRate
    template_name = 'repaid.html'

    # 計算処理
    def form_valid(self, form):
        data = form.cleaned_data
        borrow = data['borrow']
        borrow *= 10000
        year = data['year']
        select = data['select']
        repaid_type = data['repaid_type']
        if select == '0':
            interest_rate = data['interest']
        else:
            interest_rate = float(self.request.POST['bank_rate'])
        if interest_rate == 0 or interest_rate is None:
            interest_rate = 0
            ctxt = self.get_context_data(interest_rate=interest_rate, form=form)
            return self.render_to_response(ctxt)
        if repaid_type == '0':
            js_data = self.create_Pcsv(borrow, interest_rate, year)
            amount_repaid = self.paid(borrow, interest_rate, year)
            total_repaid = self.total_repaid(amount_repaid)
            interest = self.interest(borrow, total_repaid)
            data = self.read('Pdata.csv', year)
            # self.csv_to_excel('Pdata.csv')
            amount_repaid = self.com(amount_repaid)
        else:
            js_data = self.create_PIcsv(borrow, interest_rate, year)
            data = self.read('PIdata.csv', year)
            # self.csv_to_excel('PIdata.csv')
            amount_repaid = data[0][1]
            total_repaid = self.total_PIrepaid(interest_rate, borrow, year)
            interest = total_repaid - borrow
        ctxt = self.get_context_data(interest_rate=interest_rate, borrow=self.com(borrow), amount_repaid=amount_repaid,
                                     total_repaid=self.com(total_repaid), interest=self.com(interest),
                                     data=data,  form=form, js_data=js_data)
        return self.render_to_response(ctxt)

    # templatesにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_info = self.get_bank_info()
        context['BankInfo'] = bank_info
        return context

    # ログイン情報をform.pyに送る
    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        user_name = self.get_userid()
        print(f'user_id　view: {user_name}')
        kwgs["user"] = user_name
        return kwgs

    # 金利作成
    def get_bank_info(self):
        user_name = self.get_userid()
        json_encode = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id=user_name)
        bank_info = []
        for i in json_encode:
            bank_data = {
                "bank_id": i.bank_id_id, "変動金利型": i.floating,
                "固定金利選択型01年": i.fixed_1, "固定金利選択型02年": i.fixed_2, "固定金利選択型03年": i.fixed_3,
                "固定金利選択型05年": i.fixed_5, "固定金利選択型07年": i.fixed_7, "固定金利選択型10年": i.fixed_10,
                "固定金利選択型15年": i.fixed_15, "固定金利選択型20年": i.fixed_20, "固定金利選択型30年": i.fixed_30,
                '全期間固定金利型11〜15年': i.fix_10to15, '全期間固定金利型16〜20年': i.fix_15to20,
                '全期間固定金利型21〜25年': i.fix_20to25, '全期間固定金利型26〜30年': i.fix_25to30,
                '全期間固定金利型31〜35年': i.fix_30to35
                    }
            bank_info.append(bank_data)
        return bank_info

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = '1'
        else:
            user_name = self.request.user
        return user_name

    # 100万あたりの返済額
    def million_per(self, interest_rate, year):
        repaid = self.paid(100, interest_rate, year)
        return int(repaid)

    # 支払い
    def paid(self, borrowed, interest_rate, year):
        n = borrowed
        i = interest_rate / 12 / 100
        t = year * 12
        repaid = n * i * ((1 + i) ** t) / (((1 + i) ** t) - 1)
        repaid = floor(repaid)
        return int(repaid)

    def com(self, i):
        i = '{:,}'.format(i)
        return i

    def P_paid(self, borrow, a_interest, a_year):
        df = {}
        interest_m = a_interest / 12 / 100
        t = a_year * 12
        pa = self.paid(borrow, a_interest, a_year)
        for n in range(t):
            interest = floor(borrow * interest_m)
            principal = pa - interest
            borrow -= principal
            if borrow < 0:
                pa += borrow
                principal += borrow
                borrow = 0
            df[f'{n + 1}'] = [pa, interest, principal, borrow]
        return df

    # 元金均等
    def PI_paid(self, borrow, _interest, _year):
        df = {}
        t = _year * 12
        principal = floor(borrow / t)
        interest_m = _interest / 12 / 100
        for n in range(t):
            interest = floor(borrow * interest_m)
            pay = interest + principal
            borrow -= principal
            if n == 419:
                pay += borrow
                principal += borrow
                borrow = 0
            df[f'{n + 1}'] = [pay, interest, principal, borrow]
        return df

    # 元金均等
    def create_PIcsv(self, borrow, interest, year):
        paid = self.PI_paid(borrow, interest, year)
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
        df.to_csv('PIdata.csv')
        # filename = self.create_graph('PIdata.csv', 'PIgraph')
        return js

    # 元利均等
    def create_Pcsv(self, borrow, interest, year):
        paid = self.P_paid(borrow, interest, year)
        month = []
        interest_list = []
        principal_list = []
        total_list = []
        print(paid)
        for key, value in paid.items():
            month.append(key)
            interest_list.append(value[1])
            principal_list.append(value[2])
            total_list.append(value[0])
        js = [month, interest_list, principal_list, total_list]
        df = pd.DataFrame(paid)
        df.to_csv('Pdata.csv')
        # filename = self.create_graph('Pdata.csv', 'Pgraph')
        return js

    # 返済総額(元利)
    def total_repaid(self, repaid):
        TotalRepaid = repaid * 420
        return TotalRepaid

    # 返済総額(元金)
    def total_PIrepaid(self, interest_rate, borrowed, year):
        times = year * 12
        principal = floor(borrowed / times)
        interest_m = interest_rate / 12 / 100
        total_repaid = borrowed
        for n in range(times):
            interest = floor(borrowed * interest_m)
            total_repaid += interest
            borrowed -= principal
        return int(total_repaid)

    # 利息分
    def interest(self, borrowed, total_repaid):
        t = int(total_repaid)
        n = int(t - borrowed)
        return n

    def read(self, csv, year):
        df = pd.read_csv(csv)
        li = ["1", '13', '25', '49', '109', '228', '349', '409']
        years = [' 1年目', '  2年目', ' 3年目', ' 5年目', '10年目', '20年目', '30年目',
                 '35年目']
        contents = {}
        if year == 35:
            count = 7
        elif year >= 30:
            count = 6
        elif year >= 20:
            count = 5
        elif year >= 10:
            count = 4
        elif year >= 5:
            count = 3
        elif year >= 2:
            count = 2
        elif year >= 1:
            count = 1
        else:
            count = 0
        for n in range(count + 1):
            ind = [years[n]]
            for i in range(4):
                ind.append(str(self.com(df.iloc[i][li[n]])))
            contents[n] = ind
        return contents


class CreateInterestView(generic.FormView, LoginRequiredMixin):

    form_class = CreateInterestForm
    template_name = 'create_interest.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        form.save(user_name=self.request.user)

        # interest_rate.user = self.request.user
        # interest_rate.save()
        messages.success(self.request, '金利情報を追加しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '金利情報を追加できませんでした')
        return super().form_invalid(form)


class ChoiceBankView(generic.FormView, LoginRequiredMixin):

    form_class = ChoiceBankForm
    model = Bank
    template_name = 'choice_bank.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:change_interest', kwargs={'pk': self.request.POST['bank']})

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        user_name = self.get_userid()
        kwgs["user"] = user_name
        return kwgs

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = '1'
        else:
            user_name = self.request.user
        return user_name


class ChangeInterestView(generic.UpdateView, LoginRequiredMixin):

    form_class = ChangeInterestForm
    model = InterestRate
    template_name = 'change_interest.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        messages.success(self.request, '金利情報を変更しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '金利情報を変更できませんでした')
        return super().form_invalid(form)


class DeleteBankView(generic.FormView, LoginRequiredMixin):

    form_class = ChoiceBankForm
    model = Bank
    template_name = 'delete_bank.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:delete_confirm', kwargs={'pk': int(self.request.POST['bank'])})

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        user_name = self.get_userid()
        kwgs["user"] = user_name
        return kwgs

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = '1'
        else:
            user_name = self.request.user
        return user_name


class DeleteConfirmView(LoginRequiredMixin, generic.DeleteView):

    model = Bank
    template_name = 'delete_confirm.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '銀行データを削除しました')
        return super().delete(request, *args, **kwargs)
