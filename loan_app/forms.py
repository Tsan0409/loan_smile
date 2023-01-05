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
    select = forms.ChoiceField(label='属性', widget=forms.RadioSelect(
        attrs={'onchange': "on_radio();"}), choices=CHOICE_RADIO, initial=0)
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
        self.fields['choice'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id=user)

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
    year = forms.IntegerField(label=' 年数', min_value=1, max_value=50)
    select = forms.ChoiceField(label='属性', choices=CHOICE_RADIO, initial=0,
                               widget=forms.RadioSelect(
                                   attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(label='金利', min_value=0.01, required=False)
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(), required=False,
                                  widget=forms.widgets.Select(
                                      attrs={
                                          'onchange': "select_da(interest_ra);"}),
                                  label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            copy = str(field)
            if 'ChoiceField' in copy:
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'

        # ユーザー別の銀行データを渡す
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id=user)

    def clean(self):
        data = super().clean()
        print(data)
        # 途中でエラーを起こすz
        radio = data['select']
        print(radio)
        if radio == '1':
            data[4] = 0
        return data


class RequiredIncomeForm(forms.Form):

    user_name = None
    CHOICE_RADIO = [('0', '金利を入力'),
                    ('1', '金融機関から選択'), ]

    borrow = forms.IntegerField(label='借入額')
    repayment_ratio = forms.IntegerField(label='借入比率')
    year = forms.IntegerField(label=' 年数', min_value=1, max_value=50)
    select = forms.ChoiceField(label='属性', choices=CHOICE_RADIO, initial=0,
                               widget=forms.RadioSelect(
                                   attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(label='金利', required=False, min_value=0.01)
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(), required=False,
                                  widget=forms.widgets.Select(
                                      attrs={
                                          'onchange': "select_da(interest_ra);"}),
                                  label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            copy = str(field)
            if 'ChoiceField' in copy:
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'

        # ユーザー別の銀行データを渡す
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id=user)


class RepaidForm(forms.Form):
    user_name = None
    CHOICE_RADIO = [('0', '金利を入力'),
                    ('1', '金融機関から選択'), ]

    CHOICE_TYPE = [('0', '元利均等返済'),
                   ('1', '元金均等返済'), ]
    borrow = forms.IntegerField(label='借入額')
    year = forms.IntegerField(label=' 年数', min_value=1, max_value=50)
    repaid_type = forms.ChoiceField(label='返済タイプ', choices=CHOICE_TYPE,
                                    initial=0,
                                    widget=forms.RadioSelect())
    select = forms.ChoiceField(label='属性', choices=CHOICE_RADIO, initial=0,
                               widget=forms.RadioSelect(
                                   attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(label='金利', required=False, min_value=0.01)
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(), required=False,
                                  widget=forms.widgets.Select(
                                      attrs={
                                          'onchange': "select_da(interest_ra);"}),
                                  label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            copy = str(field)
            if 'ChoiceField' in copy:
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'

        # ユーザー別の銀行データを渡す
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id=user)


class CreateInterestForm(forms.Form):

    bank_name = forms.CharField(label='銀行名前')
    floating = forms.FloatField(label='変動金利型', min_value=0)
    fixed_1 = forms.FloatField(label='固定金利選択型01年', min_value=0)
    fixed_2 = forms.FloatField(label='固定金利選択型02年', min_value=0)
    fixed_3 = forms.FloatField(label='固定金利選択型05年', min_value=0)
    fixed_5 = forms.FloatField(label='固定金利選択型05年', min_value=0)
    fixed_7 = forms.FloatField(label='固定金利選択型07年', min_value=0)
    fixed_10 = forms.FloatField(label='固定金利選択型10年', min_value=0)
    fixed_15 = forms.FloatField(label='固定金利選択型15年', min_value=0)
    fixed_20 = forms.FloatField(label='固定金利選択型20年', min_value=0)
    fixed_30 = forms.FloatField(label='固定金利選択型30年', min_value=0)
    fix_10to15 = forms.FloatField(label='全期間固定金利型11〜15年', min_value=0)
    fix_15to20 = forms.FloatField(label='全期間固定金利型16〜20年', min_value=0)
    fix_20to25 = forms.FloatField(label='全期間固定金利型21〜25年', min_value=0)
    fix_25to30 = forms.FloatField(label='全期間固定金利型26〜30年', min_value=0)
    fix_30to35 = forms.FloatField(label='全期間固定金利型31〜35年', min_value=0)

    def save(self, user_name):
        data = self.cleaned_data
        bank = Bank(bank_name=data['bank_name'], user_id=user_name)
        bank.save()
        bank_id = Bank.objects.get(bank_name=data['bank_name'], user_id=user_name)
        interest = InterestRate(bank_id=bank_id, floating=data['floating'],
                                fixed_1=data['fixed_1'], fixed_2=data['fixed_2'],
                                fixed_3=data['fixed_3'], fixed_5=data['fixed_5'],
                                fixed_7=data['fixed_7'], fixed_10=data['fixed_10'],
                                fixed_15=data['fixed_15'], fixed_20=data['fixed_20'],
                                fixed_30=data['fixed_30'], fix_10to15=data['fix_10to15'],
                                fix_15to20=data['fix_15to20'], fix_20to25=data['fix_20to25'],
                                fix_25to30=data['fix_25to30'], fix_30to35=data['fix_30to35']
                                )
        interest.save()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            copy = str(field)
            if 'ChoiceField' in copy:
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'


class ChoiceBankForm(forms.Form):
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(),
                                  widget=forms.widgets.Select(), label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs),

        # Classの付与
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-text'

        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id=user)


class ChangeInterestForm(forms.ModelForm):
    class Meta:
        model = InterestRate
        fields = (
            'floating', 'fixed_1', 'fixed_2', 'fixed_3',
            'fixed_5', 'fixed_7', 'fixed_10', 'fixed_15',
            'fixed_20', 'fixed_30', 'fix_10to15', 'fix_15to20',
            'fix_20to25', 'fix_25to30', 'fix_30to35'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-text'
