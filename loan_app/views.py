import logging

import params as params
import requests
from django.core import serializers
from django.shortcuts import render, redirect

from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse


from .forms import InquiryForm, SampleForm, BorrowAbleForm,\
    RequiredIncomeForm, RepaidForm, CreateInterestForm,\
    ChangeInterestForm, ChoiceBankForm, CompareInterestForm, \
    CreateOptionForm, ChoiceOptionForm, ChangeOptionForm
from .models import Bank, InterestRate, Option
from .modules import module

import pandas as pd
from decimal import Decimal


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
        income = data['income']
        repayment_ratio = data['repayment_ratio']
        debt = data['debt']
        year = data['year']
        select = data['select']
        if select == '0':
            interest_rate = float(Decimal(data['interest']))
            option_rate = 0
            sum_rate = interest_rate
        else:
            interest_rate = Decimal(self.request.POST['bank_rate'])
            option_rate = Decimal(self.request.POST['bank_option'])
            sum_rate = float(interest_rate + option_rate)
        million_per = module.per_million(sum_rate, year)
        borrowable = module.com(module.borrowable(income, repayment_ratio, debt, million_per))
        ctxt = self.get_context_data(interest_rate=interest_rate, borrowable=borrowable, option_rate=option_rate,  form=form)
        return self.render_to_response(ctxt)

    # フォームにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_info = self.get_bank_info()
        context['BankInfo'] = bank_info
        bank_option = self.get_bank_option()
        context['BankOption'] = bank_option
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
        json_encode = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id__in=user_name)
        bank_info = module.create_bank_dict(json_encode)
        return bank_info

    # option_data
    def get_bank_option(self):
        user_name = self.get_userid()
        json_encode = Option.objects.all().select_related('bank_id').filter(bank_id__user_id__in=user_name)
        bank_option = module.create_option_dict(json_encode)
        return bank_option

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = ['1']
        else:
            user_name = [self.request.user, '1']
        return user_name


class RequiredIncomeView(generic.FormView, LoginRequiredMixin):

    form_class = RequiredIncomeForm
    model = InterestRate
    template_name = 'required_income.html'

    # 計算処理
    def form_valid(self, form):
        data = form.cleaned_data
        borrow = data['borrow']
        repayment_ratio = data['repayment_ratio']
        year = data['year']
        select = data['select']
        if select == '0':
            interest_rate = float(Decimal(data['interest']))
            option_rate = 0
            sum_rate = interest_rate
        else:
            interest_rate = Decimal(self.request.POST['bank_rate'])
            option_rate = Decimal(self.request.POST['bank_option'])
            sum_rate = float(interest_rate + option_rate)
        per_million = module.per_million(sum_rate, year)
        required_income = module.com(module.required_income(repayment_ratio, per_million, borrow))
        ctxt = self.get_context_data(interest_rate=interest_rate, option_rate=option_rate, required_income=required_income, form=form)
        return self.render_to_response(ctxt)

    # フォームにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_info = self.get_bank_info()
        context['BankInfo'] = bank_info
        bank_option = self.get_bank_option()
        context['BankOption'] = bank_option
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
        json_encode = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id__in=user_name)
        print(json_encode)
        bank_info = module.create_bank_dict(json_encode)
        return bank_info

    # option_data
    def get_bank_option(self):
        user_name = self.get_userid()
        json_encode = Option.objects.all().select_related('bank_id').filter(bank_id__user_id__in=user_name)
        bank_option = module.create_option_dict(json_encode)
        return bank_option


    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = ['1']
        else:
            user_name = [self.request.user, '1']
        return user_name


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
            interest_rate = float(Decimal(data['interest']))
            option_rate = 0
            sum_rate = interest_rate
        else:
            interest_rate = Decimal(self.request.POST['bank_rate'])
            option_rate = Decimal(self.request.POST['bank_option'])
            sum_rate = float(interest_rate + option_rate)
        # 元金均等返済方
        if repaid_type == '0':
            js_data = module.create_Pcsv(borrow, sum_rate, year)
            amount_repaid = module.cal_paid(borrow, sum_rate, year)
            total_repaid = module.total_repaid(amount_repaid, year)
            interest = module.cal_interest(borrow, total_repaid)
            data = self.read('Pdata.csv', year)
            # self.csv_to_excel('Pdata.csv')
            amount_repaid = module.com(amount_repaid)
        # 元利均等返済
        else:
            js_data = module.create_PIcsv(borrow, sum_rate, year)
            data = self.read('PIdata.csv', year)
            # self.csv_to_excel('PIdata.csv')
            amount_repaid = data[0][1]
            total_repaid = module.total_PIrepaid(sum_rate, borrow, year)
            interest = total_repaid - borrow
        ctxt = self.get_context_data(interest_rate=interest_rate, borrow=module.com(borrow), amount_repaid=amount_repaid,
                                     total_repaid=module.com(total_repaid), interest=module.com(interest),
                                     option_rate=option_rate, data=data,  form=form, js_data=js_data)
        return self.render_to_response(ctxt)

    # templatesにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_info = self.get_bank_info()
        context['BankInfo'] = bank_info
        bank_option = self.get_bank_option()
        context['BankOption'] = bank_option
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
        json_encode = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id__in=user_name)
        print(json_encode)
        bank_info = module.create_bank_dict(json_encode)
        return bank_info

    # option_data
    def get_bank_option(self):
        user_name = self.get_userid()
        json_encode = Option.objects.all().select_related('bank_id').filter(
            bank_id__user_id__in=user_name)
        bank_option = module.create_option_dict(json_encode)
        return bank_option

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = ['1']
        else:
            user_name = [self.request.user, '1']
        return user_name

    # csvの読み込み
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
                ind.append(str(module.com(df.iloc[i][li[n]])))
            contents[n] = ind
        return contents


class CompareInterestView(generic.FormView, LoginRequiredMixin):

    template_name = 'compare_interest.html'
    models = InterestRate
    form_class = CompareInterestForm

    def form_valid(self, form):
        data = form.cleaned_data
        repaid_type = data['select']
        user_name = self.get_userid()
        interest_rate = InterestRate.objects.filter(bank_id__user_id__in=user_name)\
            .exclude().values('bank_id_id__bank_name', repaid_type).order_by(repaid_type)
        for i in interest_rate:
            i['interest'] = i[repaid_type]
            if i[repaid_type] == 0:
                i['paid'] = '0'
            else:
                paid = module.com(module.cal_paid(30000000, i['interest'], 35))
                i['paid'] = paid
        ctxt = self.get_context_data(form=form, interest_rate=interest_rate, repaid_type=repaid_type)
        return self.render_to_response(ctxt)

    # ユーザー分
    def get_userid(self):
        if not self.request.user.is_authenticated:
            user_name = ['1']
        else:
            user_name = [self.request.user, '1']
        return user_name



class CreateInterestView(generic.FormView, LoginRequiredMixin):

    form_class = CreateInterestForm
    template_name = 'create_interest.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        form.save(user_name=self.request.user)
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
        if 'delete' in self.request.POST:
            return reverse_lazy('loan_app:delete_bank', kwargs={'pk': int(self.request.POST['bank'])})
        else:
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


class DeleteBankView(LoginRequiredMixin, generic.DeleteView):

    model = Bank
    template_name = 'delete.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        messages.success(self.request, '銀行データを削除しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '銀行データを削除できませんでした')
        return super().form_invalid(form)


class CreateOptionView(LoginRequiredMixin, generic.FormView):

    form_class = CreateOptionForm
    model = Bank
    template_name = 'create_option.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'オプションを追加しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'オプションを追加できませんでした')
        return super().form_invalid(form)

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


class ChoiceOptionView(generic.FormView, LoginRequiredMixin):

    form_class = ChoiceOptionForm
    model = Bank
    template_name = 'choice_option.html'

    def get_success_url(self):
        if 'delete' in self.request.POST:
            return reverse_lazy('loan_app:delete_option',
                                kwargs={'pk': self.request.POST.get('bank_option')})
        else:
            return reverse_lazy('loan_app:change_option',
                                kwargs={'pk': self.request.POST.get('bank_option')})

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

    # フォームにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_option = self.get_bank_option()
        context['BankOption'] = bank_option
        return context

    # option_data
    def get_bank_option(self):
        user_name = self.get_userid()
        json_encode = Option.objects.all().select_related('bank_id').filter(bank_id__user_id=user_name)
        bank_option = module.create_option_dict(json_encode)
        print(bank_option)
        return bank_option


class ChangeOptionView(generic.UpdateView, LoginRequiredMixin):

    form_class = ChangeOptionForm
    model = Option
    template_name = 'change_interest.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        messages.success(self.request, 'オプションを変更しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'オプションを変更できませんでした')
        return super().form_invalid(form)


class DeleteOptionView(LoginRequiredMixin, generic.DeleteView):

    model = Option
    template_name = 'delete.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        messages.success(self.request, 'オプションを削除しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'オプションを削除できませんでした')
        return super().form_invalid(form)
