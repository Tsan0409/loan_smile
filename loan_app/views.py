import logging
import json


import params as params
import requests
from django.core import serializers
from django.shortcuts import render

from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse


from .forms import InquiryForm, SampleForm, BorrowAbleForm
from .models import Bank, InterestRate, Option


from math import floor

logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = 'index.html'


# サンプル(form)アップデートで使うであろう
class SamplebView(generic.ListView, LoginRequiredMixin):
    model = Bank
    template_name = 'sampleB.html'

    def get_queryset(self):
        print(f'{self.request.user.is_authenticated}')
        if not self.request.user.is_authenticated:
            user_name = '1'
        else:
            user_name = self.request.user
        interest = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id=user_name)
        return interest



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
        income = data['income']
        repayment_ratio = data['repayment_ratio']
        debt = data['debt']
        year = data['year']
        select = data['select']
        if select == '0':
            interest_rate = data['interest']
        else:
            interest_rate = float(self.request.POST['bank_rate'])
            print(f"POST DATA: {self.request.POST['bank_rate']}")
            print(f'request form: {self.request.form.get("bank_rate")}')
        million_per = self.million_per(interest_rate, year)
        borrowable = self.borrowable(income, repayment_ratio, debt, million_per)
        ctxt = self.get_context_data(borrowable=borrowable, form=form)
        return self.render_to_response(ctxt)

    # フォームにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_info = self.get_bank_info()
        context['BankInfo'] = bank_info
        return context

    # 金利作成
    def get_bank_info(self):
        user_name = self.get_userid()
        json_encode = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id=user_name)
        print(json_encode)
        bank_info = []
        for i in json_encode:
            print(i)
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
        print(bank_info)
        return bank_info

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = '1'
        else:
            user_name = self.request.user
        return user_name

    # ログイン情報をform.pyに送る
    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        user_name = self.get_userid()
        print(f'user_id　view: {user_name}')
        kwgs["user"] = user_name
        return kwgs

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
        if t > 420:
            return print('error')
        repaid = n * i * ((1 + i) ** t) / (((1 + i) ** t) - 1)
        repaid = floor(repaid)

        return int(repaid)


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
