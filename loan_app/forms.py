from django import forms
from django.core.exceptions import ValidationError
from .models import Bank, InterestRate, Option

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
        to_list = [os.environ.get('FROM_EMAIL')]
        cc_list = [email]
        message = EmailMessage(subject=subject, body=message,
                               from_email=from_email, to=to_list, cc=cc_list)
        message.send()


class BorrowAbleForm(forms.Form):
    user_name = None
    CHOICE_RADIO = [('0', '金利を入力'),
                    ('1', '金融機関から選択'), ]

    income = forms.IntegerField(label='年収', max_value=100000, min_value=1)
    repayment_ratio = forms.IntegerField(label='借入比率', max_value=40, min_value=1)
    debt = forms.IntegerField(label='負債', max_value=1000000, min_value=0)
    year = forms.IntegerField(label='年数', min_value=1, max_value=50)
    select = forms.ChoiceField(label='属性', choices=CHOICE_RADIO, initial=0,
                               widget=forms.RadioSelect(
                                   attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(label='金利', required=False, min_value=0.0001, max_value=25)
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(), required=False,
                                  widget=forms.widgets.Select(attrs={
                                      'onchange': "select_da(interest_ra);"}),
                                  label='銀行名')

    def __init__(self, bank_rate, bank_option, user=None, *args, **kwargs):
        self.bank_rate = bank_rate
        self.bank_option = bank_option
        super().__init__(*args, **kwargs)

        PH = {'income': ' 600  (万円)',
              'repayment_ratio': ' 35  (%)',
              'debt': ' 20,000  (円/月)',
              'year': ' 35  (年)',
              'interest': ' 0.545  (%)'
              }

        # Classの付与
        for field_name, field_value in self.fields.items():
            copy = str(field_value)
            if 'ChoiceField' in copy:
                field_value.widget.attrs['class'] = 'select_radio'
            else:
                field_value.widget.attrs['class'] = 'form-text'
                field_value.widget.attrs['placeholder'] = PH[f'{field_name}']

        # ユーザー別の銀行データを渡す
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)

    def clean(self):
        super(BorrowAbleForm, self).clean()
        data = self.cleaned_data
        if data['select'] == '0':
            if 'interest' in data and data['interest'] is None:
                data['interest'] = 0
                self._errors['interest'] = self.error_class([
                    'このフィールドは必須です。'])
        else:
            if self.bank_rate is None:
                self._errors['bank'] = self.error_class([
                    '金利が選択されていません。'])
            elif self.bank_option is None:
                self._errors['bank'] = self.error_class([
                    'オプションが選択されていません。'])
            elif self.bank_option + self.bank_rate <= 0:
                self._errors['bank'] = self.error_class([
                    '金利とオプションの合計は 0 以上にしてください。'])
            data['bank_rate'] = self.bank_rate
            data['bank_option'] = self.bank_option
        return self.cleaned_data


class RequiredIncomeForm(forms.Form):
    user_name = None
    CHOICE_RADIO = [('0', '金利を入力'),
                    ('1', '金融機関から選択'), ]

    borrow = forms.IntegerField(label='借入額', min_value=1, max_value=9999999)
    repayment_ratio = forms.IntegerField(label='借入比率', min_value=1, max_value=40)
    year = forms.IntegerField(label=' 年数', min_value=1, max_value=50)
    select = forms.ChoiceField(label='属性', choices=CHOICE_RADIO, initial=0,
                               widget=forms.RadioSelect(
                                   attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(label='金利', required=False, min_value=0.0001, max_value=25)
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(), required=False,
                                  widget=forms.widgets.Select(
                                      attrs={
                                          'onchange': "select_da(interest_ra);"}),
                                  label='銀行名')

    def __init__(self, bank_rate, bank_option, user=None, *args, **kwargs):
        self.bank_rate = bank_rate
        self.bank_option = bank_option
        super().__init__(*args, **kwargs)

        PH = {'borrow': ' 3000  (万円)',
              'repayment_ratio': ' 35  (%)',
              'year': ' 35  (年)',
              'interest': ' 0.545  (%)'
              }

        # Classの付与
        for field_name, field_value in self.fields.items():
            copy = str(field_value)
            if 'ChoiceField' in copy:
                field_value.widget.attrs['class'] = 'select_radio'
            else:
                field_value.widget.attrs['class'] = 'form-text'
                field_value.widget.attrs['placeholder'] = PH[f'{field_name}']

        # ユーザー別の銀行データを渡す
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)

    def clean(self):
        super(RequiredIncomeForm, self).clean()
        data = self.cleaned_data
        if data['select'] == '0':
            if 'interest' in data and data['interest'] is None:
                data['interest'] = 0
                self._errors['interest'] = self.error_class([
                    'このフィールドは必須です。'])
        else:
            if self.bank_rate is None:
                self._errors['bank'] = self.error_class([
                    '金利が選択されていません。'])
            elif self.bank_option is None:
                self._errors['bank'] = self.error_class([
                    'オプションが選択されていません。'])
            elif self.bank_option + self.bank_rate <= 0:
                self._errors['bank'] = self.error_class([
                    '金利とオプションの合計は 0 以上にしてください。'])
            data['bank_rate'] = self.bank_rate
            data['bank_option'] = self.bank_option
        return self.cleaned_data


class RepaidForm(forms.Form):
    user_name = None
    CHOICE_RADIO = [('0', '金利を入力'),
                    ('1', '金融機関から選択'), ]

    CHOICE_TYPE = [('0', '元利均等返済'),
                   ('1', '元金均等返済'), ]
    borrow = forms.IntegerField(label='借入額', min_value=1, max_value=9999999)
    year = forms.IntegerField(label=' 年数', min_value=1, max_value=50)
    repaid_type = forms.ChoiceField(label='返済タイプ', choices=CHOICE_TYPE,
                                    initial=0,
                                    widget=forms.RadioSelect())
    select = forms.ChoiceField(label='属性', choices=CHOICE_RADIO, initial=0,
                               widget=forms.RadioSelect(
                                   attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(label='金利', required=False, min_value=0.0001,
                                max_value=25)
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(), required=False,
                                  widget=forms.widgets.Select(
                                      attrs={
                                          'onchange': "select_da(interest_ra);"}),
                                  label='銀行名')

    def __init__(self, bank_rate, bank_option, user=None, *args, **kwargs):
        self.bank_rate = bank_rate
        self.bank_option = bank_option
        super().__init__(*args, **kwargs)

        PH = {'borrow': ' 3000  (万円)',
              'year': ' 35  (年)',
              'interest': ' 0.545  (%)'
              }

        # Classの付与
        for field_name, field_value in self.fields.items():
            copy = str(field_value)
            if 'ChoiceField' in copy:
                field_value.widget.attrs['class'] = 'select_radio'
            else:
                field_value.widget.attrs['class'] = 'form-text'
                field_value.widget.attrs['placeholder'] = PH[f'{field_name}']

        # ユーザー別の銀行データを渡す
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)

    def clean(self):
        super(RepaidForm, self).clean()
        data = self.cleaned_data
        if data['select'] == '0':
            if 'interest' in data and data['interest'] is None:
                data['interest'] = 0
                self._errors['interest'] = self.error_class([
                    'このフィールドは必須です。'])
        else:
            if self.bank_rate is None:
                self._errors['bank'] = self.error_class([
                    '金利が選択されていません。'])
            elif self.bank_option is None:
                self._errors['bank'] = self.error_class([
                    'オプションが選択されていません。'])
            elif self.bank_option + self.bank_rate <= 0:
                self._errors['bank'] = self.error_class([
                    '金利とオプションの合計は 0 以上にしてください。'])
            data['bank_rate'] = self.bank_rate
            data['bank_option'] = self.bank_option
        return self.cleaned_data


class CompareInterestForm(forms.Form):
    CHOICE_REPAID = [
        ('floating', '変動金利型'),
        ('fixed_1', '固定金利選択型01年'),
        ('fixed_2', '固定金利選択型02年'),
        ('fixed_3', '固定金利選択型03年'),
        ('fixed_5', '固定金利選択型05年'),
        ('fixed_7', '固定金利選択型07年'),
        ('fixed_10', '固定金利選択型10年'),
        ('fixed_15', '固定金利選択型15年'),
        ('fixed_20', '固定金利選択型20年'),
        ('fixed_30', '固定金利選択型30年'),
        ('fix_10to15', '全期間固定金利型11〜15年'),
        ('fix_15to20', '全期間固定金利型16〜20年'),
        ('fix_20to25', '全期間固定金利型21〜25年'),
        ('fix_25to30', '全期間固定金利型26〜30年'),
        ('fix_30to35', '全期間固定金利型31〜35年'),
    ]

    select = forms.ChoiceField(label='属性', choices=CHOICE_REPAID,
                               widget=forms.widgets.Select(
                                   attrs={'class': 'form-text'}
                               ))


class CreateInterestForm(forms.Form):
    bank_name = forms.CharField(label='銀行名前')
    floating = forms.FloatField(label='変動金利型',
                                min_value=0, max_value=25)
    fixed_1 = forms.FloatField(label='固定金利選択型01年',
                               min_value=0, max_value=25)
    fixed_2 = forms.FloatField(label='固定金利選択型02年',
                               min_value=0, max_value=25)
    fixed_3 = forms.FloatField(label='固定金利選択型03年',
                               min_value=0, max_value=25)
    fixed_5 = forms.FloatField(label='固定金利選択型05年',
                               min_value=0, max_value=25)
    fixed_7 = forms.FloatField(label='固定金利選択型07年',
                               min_value=0, max_value=25)
    fixed_10 = forms.FloatField(label='固定金利選択型10年',
                                min_value=0, max_value=25)
    fixed_15 = forms.FloatField(label='固定金利選択型15年',
                                min_value=0, max_value=25)
    fixed_20 = forms.FloatField(label='固定金利選択型20年',
                                min_value=0, max_value=25)
    fixed_30 = forms.FloatField(label='固定金利選択型30年',
                                min_value=0, max_value=25)
    fix_10to15 = forms.FloatField(label='全期間固定金利型11〜15年',
                                  min_value=0, max_value=25)
    fix_15to20 = forms.FloatField(label='全期間固定金利型16〜20年',
                                  min_value=0, max_value=25)
    fix_20to25 = forms.FloatField(label='全期間固定金利型21〜25年',
                                  min_value=0, max_value=25)
    fix_25to30 = forms.FloatField(label='全期間固定金利型26〜30年',
                                  min_value=0, max_value=25)
    fix_30to35 = forms.FloatField(label='全期間固定金利型31〜35年',
                                  min_value=0, max_value=25)

    def save(self, user_name):
        data = self.cleaned_data
        bank = Bank(bank_name=data['bank_name'], user_id=user_name)
        bank.save()

        bank_id = Bank.objects.get(
            bank_name=data['bank_name'], user_id=user_name
        )
        interest = InterestRate(
            bank_id=bank_id, floating=data['floating'],
            fixed_1=data['fixed_1'], fixed_2=data['fixed_2'],
            fixed_3=data['fixed_3'], fixed_5=data['fixed_5'],
            fixed_7=data['fixed_7'], fixed_10=data['fixed_10'],
            fixed_15=data['fixed_15'], fixed_20=data['fixed_20'],
            fixed_30=data['fixed_30'], fix_10to15=data['fix_10to15'],
            fix_15to20=data['fix_15to20'], fix_20to25=data['fix_20to25'],
            fix_25to30=data['fix_25to30'], fix_30to35=data['fix_30to35']
        )
        interest.save()

    def __init__(self, user, *args, **kwargs):
        self.login_user = user
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            copy = str(field)
            if 'ChoiceField' in copy:
                field.widget.attrs['class'] = 'select_radio'
            else:
                field.widget.attrs['class'] = 'form-text'

    # 同じ名前の金融機関を通さない
    def clean(self):
        super(CreateInterestForm, self).clean()
        data = self.cleaned_data
        user = self.login_user[0]
        if 'bank_name' in data:
            if Bank.objects.filter(bank_name=data['bank_name'], user_id=user).exists():
                self._errors['bank_name'] = self.error_class([
                    '同じ銀行名は作成できません。'])
        return self.cleaned_data


class ChoiceBankForm(forms.Form):
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(),
                                  widget=forms.widgets.Select(), label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs),

        # Classの付与
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-text'

        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)


class UpdateInterestForm(forms.ModelForm):
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

        # 属性の付与
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-text'
            field.widget.attrs['min'] = 0
            field.widget.attrs['max'] = 25

    # 関数で付帯したウィジェットは独自バリデーションが施されていないので、自作する必要がある
    # 最小値と最大値のバリデーション
    def clean(self):
        super(UpdateInterestForm, self).clean()
        data = self.cleaned_data
        for i in data:
            if data[i] < 0:
                self._errors[i] = self.error_class([
                    'この値は 0 以上でなければなりません。'])
            if data[i] > 25:
                self._errors[i] = self.error_class([
                    'この値は 25 以下でなければなりません。'])
        return self.cleaned_data


class CreateOptionForm(forms.ModelForm):
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(),
                                  widget=forms.widgets.Select(), label='銀行名')

    class Meta:
        model = Option
        fields = ('option_name', 'option_rate')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 属性の付与
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-text'
        self.fields['option_rate'].widget.attrs['min'] = -25
        self.fields['option_rate'].widget.attrs['max'] = 25

        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)

    def save(self, commit=True):
        data = self.cleaned_data
        option = Option(
            bank_id=data['bank'], option_name=data['option_name'],
            option_rate=data['option_rate'])
        option.save()


    def clean(self):
        super(CreateOptionForm, self).clean()
        data = self.cleaned_data

        # 同じ名前の金融機関を通さない
        if 'option_name' in data:
            if Option.objects.filter(option_name=data['option_name'],
                                     bank_id=data['bank']).exists():
                self._errors['option_name'] = self.error_class(
                    ['1つの銀行内に同じ名前のオプションは作成できません。'])


        # 最大値、最小値のバリデーション
        if 'option_rate' in data:
            if data['option_rate'] < -25:
                self._errors['option_rate'] = self.error_class([
                    'この値は -25 以上でなければなりません。'])
            if data['option_rate'] > 25:
                self._errors['option_rate'] = self.error_class([
                    'この値は 25 以下でなければなりません。'])
        return self.cleaned_data


class ChoiceOptionForm(forms.Form):
    bank = forms.ModelChoiceField(queryset=Bank.objects.none(),
                                  widget=forms.widgets.Select(attrs={
                                      'onchange': "select_option(page_type);"
                                  }), label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs),

        # Classの付与
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-text'

        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)


class UpdateOptionForm(forms.ModelForm):

    class Meta:
        model = Option
        fields = ('option_name', 'option_rate')

    def __init__(self, selected_bank, selected_option, *args, **kwargs):
        self.selected_bank = selected_bank
        self.selected_option = selected_option
        super().__init__(*args, **kwargs)

        # Classの付与
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-text'

        # 最大値、最小値の付与
        self.fields['option_rate'].widget.attrs['min'] = -25
        self.fields['option_rate'].widget.attrs['max'] = 25

    def clean(self):
        super(UpdateOptionForm, self).clean()
        data = self.cleaned_data
        bank = self.selected_bank
        # 同じ名前の金融機関を通さない

        if 'option_name' in data:
            if Option.objects.exclude(
                    option_id=self.selected_option).filter(option_name=data['option_name'],
                                                           bank_id=bank).exists():
                self._errors['option_name'] = self.error_class(
                    ['1つの銀行内に同じ名前のオプションは作成できません。'])

        # 最大値、最小値のバリデーション
        if 'option_rate' in data:
            if data['option_rate'] < -25:
                self._errors['option_rate'] = self.error_class([
                    'この値は -25 以上でなければなりません。'])
            if data['option_rate'] > 25:
                self._errors['option_rate'] = self.error_class([
                    'この値は 25 以下でなければなりません。'])
        return self.cleaned_data
