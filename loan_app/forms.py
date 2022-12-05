from django import forms
from django.core.exceptions import ValidationError
from .models import Post

import os

from django.core.mail import EmailMessage




CHOICE = {
    ('0','金利を入力'),
    ('1','金融機関から選択'),
}


class InquiryForm(forms.Form):
    name = forms.CharField(label='お名前', max_length=30)
    email = forms.EmailField(label='メールアドレス')
    title = forms.CharField(label='タイトル', max_length=30)
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['<フィールド名>'].widget.attrs['属性名']  CSS属性の操作
        self.fields['name'].widget.attrs['class'] = 'form-text'
        self.fields['name'].widget.attrs['placeholder'] = 'ここに名前を入力してください'
        self.fields['email'].widget.attrs['class'] = 'form-text'
        self.fields['email'].widget.attrs['placeholder'] = 'メールアドレスを入力してください'
        self.fields['title'].widget.attrs['class'] = 'form-text'
        self.fields['title'].widget.attrs['placeholder'] = 'タイトルを入力してください'
        self.fields['message'].widget.attrs['class'] = 'form-text'
        self.fields['message'].widget.attrs['placeholder'] = 'メッセージを入力してください'

    def send_email(self):
        # self.cleaned_data['<フィールド名>'>]
        # バリデーションを通った入力値の取得(バリデーション=必須項目の入力、入力書式, 最大値等がただし以下の確認）
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        title = self.cleaned_data['title']
        message = self.cleaned_data['message']

        subject = f'お問合せ {title}'
        message = f'送信者名: {name}\nメールアドレス: {email}\nメッセージ:\n{message}'
        from_email = os.environ.get('FROM_EMAIL')
        to_list = [
            os.environ.get('FROM_EMAIL')
        ]
        cc_list = [
            email
        ]

        message = EmailMessage(subject=subject, body=message,
                               from_email=from_email, to=to_list, cc=cc_list)
        message.send()


# サンプル
class SampleForm(forms.Form):
    text = forms.CharField(label='テキスト', widget=forms.Textarea)
    search = forms.CharField(label='検索')
    replace = forms.CharField(label='痴漢')
    select = forms.ChoiceField(label='属性', widget=forms.RadioSelect,
                               choices=CHOICE, initial=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self. fields.values():
            copy = str(field)
            print(self. fields.values())
            print(f'cコピーです{copy}')
            if 'ChoiceField' in copy:
                print('rarararara')
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'

    def clean(self):
        data = super().clean()
        print(data)
        # 途中でエラーを起こす
        text = data['text']
        print(text)
        if len(text) <= 5:
            print(ValidationError('error'))
            raise ValidationError('テキストが短過ぎます。')
        return data

# サンプル（フォームからそのまま引き継ぐことも可能）
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body']


class BorrowAbleForm(forms.Form):
    income = forms.IntegerField(label='年収')
    repayment_ratio = forms.IntegerField(label='借入比率')
    debt = forms.IntegerField(label='負債')
    year = forms.IntegerField(label=' 年数')
    select = forms.ChoiceField(label='属性', widget=forms.RadioSelect,
                               choices=CHOICE, initial=0)
    interest = forms.FloatField(label='金利', required=False)
    from_bank = forms.FloatField(label='金融機関から選択', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self. fields.values():
            copy = str(field)
            if 'ChoiceField' in copy:
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'



# def borrowable_try(**kwargs):
#     income, repayment_ratio, debt, year, radio = sys.forms_get_i(
#         li=['income', 'repayment_ratio', 'debt', 'year', 'radio', ])
#     interest_rate = sys.radio_btn(radio,
#                                   btn_list=['interest_rate', 'bank_rate'])
#     million_per = cal.million_per(interest_rate, year)
#     borrowable = cal.borrowable(income, repayment_ratio, debt, million_per)
#     bank_info = cs.user_to_rate(user.get_id()) if kwargs[
#                                                       'check'] == 'login' else cs.get_guest_data()
#     return render_template('borrowable_form.html',
#                            borrowable=cal.com(borrowable), income=income,
#                            bank_info=bank_info,
#                            interest_rate=interest_rate, debt=debt, year=year,
#                            radio=radio, repayment_ratio=repayment_ratio,
#                            bank_name=request.form.get('bank_name'))
