import logging
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages

from .forms import InquiryForm, SampleForm, PostForm, BorrowAbleForm

from math import floor

logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = 'index.html'


# サンプル
class SampleView(generic.FormView):
    form_class = SampleForm
    template_name = 'sample.html'

    def form_valid(self, form):
        # バリデーション後のデータを変数にぶち込む
        data = form.cleaned_data
        text = data['text']
        search = data['search']
        replace = data['replace']
        new_text = text.replace(search, replace)

        # htmlに渡す
        ctxt = self.get_context_data(new_text=new_text, form=form)
        return self.render_to_response(ctxt)


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



class BorrowAbleView(generic.FormView):
    form_class = BorrowAbleForm
    template_name = 'borrow_able.html'

    def form_valid(self, form):

        data = form.cleaned_data
        income = data['income']
        repayment_ratio = data['repayment_ratio']
        debt = data['debt']
        year = data['year']
        select = data['select']
        if select is '0':
            interest_rate = data['interest']
            print('金利空を選んだ')
        else:
            print('銀行からを選んだ')
            interest_rate = data['from_bank']
        million_per = self.million_per(interest_rate, year)
        borrowable = self.borrowable(income, repayment_ratio, debt, million_per)
        ctxt = self.get_context_data(borrowable=borrowable, form=form)
        return self.render_to_response(ctxt)


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
