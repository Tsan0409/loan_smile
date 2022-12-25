from django import forms
from django.core.exceptions import ValidationError
from .models import Bank, InterestRate


import os

from django.core.mail import EmailMessage


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
    CHOICE_RADIO = [
        ('0', '金利を入力'),
        ('1', '金融機関から選択'), ]

    user_name = None
    text = forms.CharField(label='テキスト', widget=forms.Textarea)
    search = forms.CharField(label='検索')
    replace = forms.CharField(label='痴漢')
    select = forms.ChoiceField(label='属性', widget=forms.RadioSelect(attrs={'onchange': "on_radio();"}), choices=CHOICE_RADIO, initial=0)
    choice = forms.ModelChoiceField(
        queryset=Bank.objects.none(),
        required=True,
        widget=forms.widgets.Select,
        label='銀行名'
    )

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f'form: {user}')
        print(self.user_name)
        print(self.fields['choice'])
        self.fields['choice'].queryset = Bank.objects.all().select_related('user_id').filter(user_id=user)

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


class BorrowAbleForm(forms.Form):

    user_name = None
    CHOICE_RADIO = [('0', '金利を入力'),
                    ('1', '金融機関から選択'), ]

    income = forms.IntegerField(label='年収')
    repayment_ratio = forms.IntegerField(label='借入比率')
    debt = forms.IntegerField(label='負債')
    year = forms.IntegerField(label=' 年数')
    select = forms.ChoiceField(label='属性', choices=CHOICE_RADIO, initial=0,
                               widget=forms.RadioSelect(
                                   attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(label='金利', required=False)
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(), required=False,
                                  widget=forms.widgets.Select(
                                   attrs={'onchange': "select_da();"}), label='銀行名')


    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            copy = str(field)
            if 'ChoiceField' in copy:
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'
        print(f'user_id　form: {user}')

        # ユーザー別の銀行データを渡す
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id=user)


class RequiredIncomeForm(forms.Form):

    user_name = None
    CHOICE_RADIO = [('0', '金利を入力'),
                    ('1', '金融機関から選択'), ]

    borrow = forms.IntegerField(label='借入額')
    repayment_ratio = forms.IntegerField(label='借入比率')
    year = forms.IntegerField(label=' 年数')
    select = forms.ChoiceField(label='属性', choices=CHOICE_RADIO, initial=0,
                               widget=forms.RadioSelect(
                                   attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(label='金利', required=False)
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(), required=False,
                                  widget=forms.widgets.Select(
                                   attrs={'onchange': "select_da();"}), label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            copy = str(field)
            if 'ChoiceField' in copy:
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'
        print(f'user_id　form: {user}')

        # ユーザー別の銀行データを渡す
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id=user)
