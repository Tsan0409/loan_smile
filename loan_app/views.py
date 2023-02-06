import logging

from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404

from .forms import InquiryForm, BorrowAbleForm, RequiredIncomeForm, RepaidForm,\
    CreateInterestForm, UpdateInterestForm, ChoiceBankForm, CompareInterestForm,\
    CreateOptionForm, ChoiceOptionForm, UpdateOptionForm
from .models import Bank, InterestRate, Option
from .modules import module

from decimal import Decimal

logger = logging.getLogger(__name__)


class UserMethods:

    # 金利を取得
    def get_bank_info(self, user):
        user_name = self.get_userid(user)
        json_encode = InterestRate.objects.all().select_related('bank_id').filter(bank_id__user_id__in=user_name)
        bank_info = module.create_bank_dict(json_encode)
        return bank_info

    # オプションを取得
    def get_bank_option(self, user):
        user_name = self.get_userid(user)
        json_encode = Option.objects.all().select_related('bank_id').filter(bank_id__user_id__in=user_name)
        bank_option = module.create_option_dict(json_encode)
        return bank_option

    # 初期userと独自userをリストで取得する
    def get_userid(self, user):
        if not self.request.user.is_authenticated:
            user_name = ['1']
        elif user == 'only_user':
            user_name = [self.request.user]
        else:
            user_name = [self.request.user, '1']
        return user_name

    # userを取得する
    def judge_user_for_model(self, kwgs):
        user_name = self.get_userid(user='only_user')
        kwgs["user"] = user_name
        return

    # 金利とオプションデータを入れる
    def send_user_data(self, context):
        bank_info = self.get_bank_info(user='')
        context['BankInfo'] = bank_info
        bank_option = self.get_bank_option(user='')
        context['BankOption'] = bank_option
        return

    # ラジオボタンと入力されたデータの処理
    def judge_radio_and_returned(self, kwgs, returned):
        if returned and returned['select'] == '1':
            if 'bank_rate' in returned:
                bank_rate = Decimal(returned['bank_rate'])
                bank_option = Decimal(returned['bank_option'])
            else:
                bank_rate = None
                bank_option = None
            kwgs["bank_rate"] = bank_rate
            kwgs["bank_option"] = bank_option
        else:
            kwgs["bank_rate"] = 0
            kwgs["bank_option"] = 0
        user_name = self.get_userid(user='')
        kwgs["user"] = user_name
        return


class IndexView(generic.TemplateView):

    template_name = 'index.html'


class InquiryView(generic.FormView):

    template_name = 'inquiry.html'
    form_class = InquiryForm
    success_url = reverse_lazy('loan_app:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました')
        logger.info(f'Inquiry sent by {form.cleaned_data["name"]}')
        return super().form_valid(form)


class BorrowAbleView(generic.FormView, UserMethods):

    form_class = BorrowAbleForm
    model = InterestRate
    template_name = 'borrow_able.html'

    def form_valid(self, form):
        data = form.cleaned_data
        income = data['income']
        repayment_ratio = data['repayment_ratio']
        debt = data['debt']
        year = data['year']
        select = data['select']
        interest_rate, option_rate, sum_rate = module.select_interest(select, data)
        million_per = module.per_million(sum_rate, year)
        borrowable = module.com(module.borrowable(income, repayment_ratio, debt, million_per))
        ctxt = self.get_context_data(interest_rate=interest_rate, borrowable=borrowable,
                                     option_rate=option_rate,  form=form)
        return self.render_to_response(ctxt)

    def form_invalid(self, form):
        messages.error(self.request, '無効な数字が入力されています')
        return super().form_invalid(form)

    # HTMLにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        self.send_user_data(context)
        return context

    # ログイン情報をform.pyに送る
    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs()
        returned = self.request.POST
        self.judge_radio_and_returned(kwgs, returned)
        return kwgs


class RequiredIncomeView(generic.FormView, UserMethods):

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
        interest_rate, option_rate, sum_rate = module.select_interest(select, data)
        per_million = module.per_million(sum_rate, year)
        required_income = module.com(module.required_income(repayment_ratio, per_million, borrow))
        ctxt = self.get_context_data(interest_rate=interest_rate, option_rate=option_rate,
                                     required_income=required_income, form=form)
        return self.render_to_response(ctxt)

    def form_invalid(self, form):
        messages.error(self.request, '無効な数字が入力されています')
        return super().form_invalid(form)

    # HTMLに金利とオプションデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        self.send_user_data(context)
        return context

    # ログイン情報をform.pyに送る
    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs()
        returned = self.request.POST
        self.judge_radio_and_returned(kwgs, returned)
        return kwgs


class RepaidView(generic.FormView, UserMethods):

    form_class = RepaidForm
    model = InterestRate
    template_name = 'repaid.html'

    def form_valid(self, form):
        data = form.cleaned_data
        borrow = data['borrow']
        borrow *= 10000
        year = data['year']
        select = data['select']
        repaid_type = data['repaid_type']
        interest_rate, option_rate, sum_rate = module.select_interest(select, data)
        # 元金均等返済方
        if repaid_type == '0':
            csv_path = module.csv_pdata_path()
            js_data = module.create_p_csv(borrow, sum_rate, year, csv_path)
            amount_repaid = module.cal_paid(borrow, sum_rate, year)
            total_repaid = module.total_repaid(amount_repaid, year)
            interest = module.cal_interest(borrow, total_repaid)
            data = module.read(csv_path, year)
            amount_repaid = module.com(amount_repaid)
        # 元利均等返済
        else:
            csv_path = module.csv_pidata_path()
            js_data = module.create_pi_csv(borrow, sum_rate, year, csv_path)
            data = module.read(csv_path, year)
            amount_repaid = data[0][1]
            total_repaid = module.total_pi_repaid(sum_rate, borrow, year)
            interest = total_repaid - borrow
        ctxt = self.get_context_data(interest_rate=interest_rate, borrow=module.com(borrow),
                                     amount_repaid=amount_repaid, total_repaid=module.com(total_repaid),
                                     interest=module.com(interest), option_rate=option_rate, data=data,
                                     form=form, js_data=js_data)
        return self.render_to_response(ctxt)

    def form_invalid(self, form):
        messages.error(self.request, '無効な数字が入力されています')
        return super().form_invalid(form)

    # HTMLにデータを送る
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        self.send_user_data(context)
        return context

    # ログイン情報をform.pyに送る
    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs()
        returned = self.request.POST
        self.judge_radio_and_returned(kwgs, returned)
        return kwgs


class CompareInterestView(generic.FormView, LoginRequiredMixin, UserMethods):

    template_name = 'compare_interest.html'
    models = InterestRate
    form_class = CompareInterestForm

    def form_valid(self, form):
        data = form.cleaned_data
        repaid_type = data['select']
        user_name = self.get_userid(user='')
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


# ユーザ以外のアクセスを制限
class OnlyYouMixin(UserPassesTestMixin):

    raise_exception = True

    def test_func(self):
        if 'bank_pk' in self.kwargs:
            loan = get_object_or_404(Bank, pk=self.kwargs['bank_pk'])
        else:
            loan = get_object_or_404(Bank, pk=self.kwargs['pk'])
        return self.request.user == loan.user_id


class CreateInterestView(LoginRequiredMixin, generic.FormView, UserMethods):

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

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs()
        self.judge_user_for_model(kwgs)
        return kwgs


class ChoiceBankView(LoginRequiredMixin, generic.FormView, UserMethods):

    form_class = ChoiceBankForm
    model = Bank
    template_name = 'choice_bank.html'

    def get_success_url(self):
        if 'delete' in self.request.POST:
            return reverse_lazy('loan_app:delete_bank',
                                kwargs={'pk': int(self.request.POST['bank'])})
        else:
            return reverse_lazy('loan_app:update_interest',
                                kwargs={'pk': self.request.POST['bank']})

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs()
        self.judge_user_for_model(kwgs)
        return kwgs


class UpdateInterestView(LoginRequiredMixin, OnlyYouMixin, generic.UpdateView):

    form_class = UpdateInterestForm
    model = InterestRate
    template_name = 'update_interest.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        messages.success(self.request, '金利情報を変更しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '金利情報を変更できませんでした')
        return super().form_invalid(form)


class DeleteBankView(LoginRequiredMixin, OnlyYouMixin, generic.DeleteView):

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


class CreateOptionView(LoginRequiredMixin, generic.FormView, UserMethods):

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
        kwgs = super().get_form_kwargs()
        self.judge_user_for_model(kwgs)
        return kwgs


class ChoiceOptionView(LoginRequiredMixin, generic.FormView, UserMethods):

    form_class = ChoiceOptionForm
    model = Bank
    template_name = 'choice_option.html'

    def get_success_url(self):
        if 'delete' in self.request.POST:
            return reverse_lazy('loan_app:delete_option',
                                kwargs={'bank_pk': self.request.POST.get('bank'),
                                        'pk': self.request.POST.get('bank_option')})
        else:
            return reverse_lazy('loan_app:update_option',
                                kwargs={'bank_pk': self.request.POST.get('bank'),
                                        'pk': self.request.POST.get('bank_option')})

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs()
        self.judge_user_for_model(kwgs)
        return kwgs

    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        bank_option = self.get_bank_option(user='only_user')
        context['BankOption'] = bank_option
        return context


class UpdateOptionView(LoginRequiredMixin, OnlyYouMixin, generic.UpdateView):

    form_class = UpdateOptionForm
    model = Option
    template_name = 'update_interest.html'

    def get_success_url(self):
        return reverse_lazy('loan_app:index')

    def form_valid(self, form):
        messages.success(self.request, 'オプションを変更しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'オプションを変更できませんでした')
        return super().form_invalid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs()
        selected_bank = Bank.objects.filter(bank_id=self.kwargs['bank_pk']).get().bank_id
        kwgs["selected_bank"] = selected_bank
        selected_option = Option.objects.filter(option_id=self.kwargs['pk']).get().option_id
        kwgs["selected_option"] = selected_option
        return kwgs


class DeleteOptionView(LoginRequiredMixin, OnlyYouMixin, generic.DeleteView):

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
