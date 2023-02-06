from django import forms
from django.core.mail import EmailMessage
from .models import Bank, InterestRate, Option

import os

CHOICE_INTEREST = [('0', '金利を入力'), ('1', '金融機関から選択'), ]


class MyMethods:

    # Form にclassとplaceholderを付与する
    def add_class(self, PH):
        for field_name, field_value in self.fields.items():
            copy = str(field_value)
            if 'ChoiceField' in copy:
                if field_name == 'select' or field_name == 'repaid_type':
                    field_value.widget.attrs['class'] = 'select_radio'
                else:
                    field_value.widget.attrs['class'] = 'form-text'
            else:
                field_value.widget.attrs['class'] = 'form-text'
                if not len(PH) == 0:
                    field_value.widget.attrs['placeholder'] = PH[
                        f'{field_name}']
        return

    # maxとminの付与
    def add_max_and_min_value(self, field_name, max_val, min_val, ):
        self.fields[f'{field_name}'].widget.attrs['min'] = min_val
        self.fields[f'{field_name}'].widget.attrs['max'] = max_val
        return

    # 独自Formのバリデーション
    def radio_validation(self, data):
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

    # 独自バリデーション
    def max_and_min_validation(self, data, max_val, min_val):
        for i in data:
            if isinstance(data[i], float):
                if data[i] < min_val:
                    self._errors[i] = self.error_class([
                        f'この値は {min_val} 以上でなければなりません。'])
                if data[i] > max_val:
                    self._errors[i] = self.error_class([
                        f'この値は {max_val} 以下でなければなりません。'])
        return

    # 独自フォームのバリデーション
    def same_bank_validation(self, data, user):
        if 'bank_name' in data:
            if Bank.objects.filter(bank_name=data['bank_name'], user_id=user).exists():
                self._errors['bank_name'] = self.error_class(['同じ銀行名は作成できません。'])
        return

    # 独自フォームのバリデーション
    def same_option_validation(self, data, bank, selected_option):
        if 'option_name' in data:
            option = Option.objects.filter(
                option_name=data['option_name'], bank_id=bank)
            if option.exclude(option_id=selected_option).exists():
                self._errors['option_name'] = self.error_class(
                    ['1つの銀行内に同じ名前のオプションは作成できません。'])
        return


class InquiryForm(forms.Form, MyMethods):

    name = forms.CharField(label='お名前', max_length=30)
    email = forms.EmailField(label='メールアドレス')
    title = forms.CharField(label='タイトル', max_length=30)
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PH = {
            'name': ' 山田　太郎',
            'email': ' smile@smile.com',
            'title': ' タイトル',
            'message': ' メッセージ'}
        self.add_class(PH)

    def send_email(self):
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


class BorrowAbleForm(forms.Form, MyMethods):

    user_name = None

    income = forms.IntegerField(
        label='年収', max_value=100000, min_value=1)
    repayment_ratio = forms.IntegerField(
        label='借入比率', max_value=40, min_value=1)
    debt = forms.IntegerField(label='負債', max_value=1000000, min_value=0)
    year = forms.IntegerField(label='年数', min_value=1, max_value=50)
    select = forms.ChoiceField(
        label='金利の入力方法', choices=CHOICE_INTEREST, initial=0,
        widget=forms.RadioSelect(attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(
        label='金利', required=False, min_value=0.0001, max_value=25)
    bank = forms.ModelChoiceField(
        queryset=Bank.objects.none(), required=False, label='銀行名',
        widget=forms.widgets.Select(attrs={'onchange': "select_da(interest_ra);"}))

    def __init__(self, bank_rate, bank_option, user=None, *args, **kwargs):
        self.bank_rate = bank_rate
        self.bank_option = bank_option
        super().__init__(*args, **kwargs)
        PH = {'income': ' 600  (万円)',
              'repayment_ratio': ' 35  (%)',
              'debt': ' 20,000  (円/月)',
              'year': ' 35  (年)',
              'interest': ' 0.545  (%)'}
        self.add_class(PH)
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)

    def clean(self):
        super(BorrowAbleForm, self).clean()
        data = self.cleaned_data
        return self.radio_validation(data)


class RequiredIncomeForm(forms.Form, MyMethods):

    user_name = None

    borrow = forms.IntegerField(
        label='借入額', min_value=1, max_value=9999999)
    repayment_ratio = forms.IntegerField(
        label='借入比率', min_value=1, max_value=40)
    year = forms.IntegerField(label=' 年数', min_value=1, max_value=50)
    select = forms.ChoiceField(
        label='金利の入力方法', choices=CHOICE_INTEREST, initial=0,
        widget=forms.RadioSelect(attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(
        label='金利', required=False, min_value=0.0001, max_value=25)
    bank = forms.ModelChoiceField(
        queryset=Bank.objects.none(), required=False, label='銀行名',
        widget=forms.widgets.Select(attrs={'onchange': "select_da(interest_ra);"}))

    def __init__(self, bank_rate, bank_option, user=None, *args, **kwargs):
        self.bank_rate = bank_rate
        self.bank_option = bank_option
        super().__init__(*args, **kwargs)
        PH = {'borrow': ' 3000  (万円)',
              'repayment_ratio': ' 35  (%)',
              'year': ' 35  (年)',
              'interest': ' 0.545  (%)'}
        self.add_class(PH)
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)

    def clean(self):
        super(RequiredIncomeForm, self).clean()
        data = self.cleaned_data
        return self.radio_validation(data)


class RepaidForm(forms.Form, MyMethods):

    user_name = None
    CHOICE_TYPE = [('0', '元利均等返済'), ('1', '元金均等返済'), ]

    borrow = forms.IntegerField(
        label='借入額', min_value=1, max_value=9999999)
    year = forms.IntegerField(
        label=' 年数', min_value=1, max_value=50)
    repaid_type = forms.ChoiceField(
        label='返済方法', choices=CHOICE_TYPE, initial=0,
        widget=forms.RadioSelect())
    select = forms.ChoiceField(
        label='金利の入力方法', choices=CHOICE_INTEREST, initial=0,
        widget=forms.RadioSelect(attrs={'onchange': "on_radio();"}))
    interest = forms.FloatField(
        label='金利', required=False, min_value=0.0001, max_value=25)
    bank = forms.ModelChoiceField(
        queryset=Bank.objects.none(), required=False, label='銀行名',
        widget=forms.widgets.Select(
            attrs={'onchange': "select_da(interest_ra);"}))

    def __init__(self, bank_rate, bank_option, user=None, *args, **kwargs):
        self.bank_rate = bank_rate
        self.bank_option = bank_option
        super().__init__(*args, **kwargs)
        PH = {'borrow': ' 3000  (万円)',
              'year': ' 35  (年)',
              'interest': ' 0.545  (%)'}
        self.add_class(PH)
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)

    def clean(self):
        super(RepaidForm, self).clean()
        data = self.cleaned_data
        return self.radio_validation(data)


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
        ('fix_30to35', '全期間固定金利型31〜35年'), ]

    select = forms.ChoiceField(
        label='金利', choices=CHOICE_REPAID,
        widget=forms.widgets.Select(attrs={'class': 'form-text'}))


class CreateInterestForm(forms.Form, MyMethods):

    bank_name = forms.CharField(label='銀行名前')
    floating = forms.FloatField(label='変動金利型')
    fixed_1 = forms.FloatField(label='固定金利選択型01年')
    fixed_2 = forms.FloatField(label='固定金利選択型02年')
    fixed_3 = forms.FloatField(label='固定金利選択型03年')
    fixed_5 = forms.FloatField(label='固定金利選択型05年')
    fixed_7 = forms.FloatField(label='固定金利選択型07年')
    fixed_10 = forms.FloatField(label='固定金利選択型10年')
    fixed_15 = forms.FloatField(label='固定金利選択型15年')
    fixed_20 = forms.FloatField(label='固定金利選択型20年')
    fixed_30 = forms.FloatField(label='固定金利選択型30年')
    fix_10to15 = forms.FloatField(label='全期間固定金利型11〜15年')
    fix_15to20 = forms.FloatField(label='全期間固定金利型16〜20年')
    fix_20to25 = forms.FloatField(label='全期間固定金利型21〜25年')
    fix_25to30 = forms.FloatField(label='全期間固定金利型26〜30年')
    fix_30to35 = forms.FloatField(label='全期間固定金利型31〜35年')

    def __init__(self, user, *args, **kwargs):
        self.login_user = user
        super().__init__(*args, **kwargs)
        PH = {
            'bank_name': 'スマイル銀行', 'floating': ' 2.475(%)', 'fixed_1': ' 0(%)',
            'fixed_2': ' 3.300(%)', 'fixed_3': ' 3.600(%)', 'fixed_5': ' 3.600(%)',
            'fixed_7': ' 3.790(%)', 'fixed_10': ' 0(%)', 'fixed_15': ' 0(%)',
            'fixed_20': ' 0(%)', 'fixed_30': ' 0(%)', 'fix_10to15': ' 2.900 (%)',
            'fix_15to20': ' 2.970(%)', 'fix_20to25': ' 3.990(%)',
            'fix_25to30': ' 2.990(%)', 'fix_30to35': ' 2.990(%)', }
        self.add_class(PH)
        for field in self.fields:
            self.add_max_and_min_value(field, 25, 0)

    def save(self, user_name):
        data = self.cleaned_data
        bank_name = data['bank_name']
        bank = Bank(bank_name=bank_name, user_id=user_name)
        bank.save()
        bank_id = Bank.objects.get(bank_name=bank_name, user_id=user_name)
        interest = InterestRate(
            bank_id=bank_id, floating=data['floating'],
            fixed_1=data['fixed_1'], fixed_2=data['fixed_2'],
            fixed_3=data['fixed_3'], fixed_5=data['fixed_5'],
            fixed_7=data['fixed_7'], fixed_10=data['fixed_10'],
            fixed_15=data['fixed_15'], fixed_20=data['fixed_20'],
            fixed_30=data['fixed_30'], fix_10to15=data['fix_10to15'],
            fix_15to20=data['fix_15to20'], fix_20to25=data['fix_20to25'],
            fix_25to30=data['fix_25to30'], fix_30to35=data['fix_30to35'])
        interest.save()

    def clean(self):
        super(CreateInterestForm, self).clean()
        data = self.cleaned_data
        user = self.login_user[0]
        self.same_bank_validation(data, user)
        self.max_and_min_validation(data, 25, 0)
        return self.cleaned_data


class ChoiceBankForm(forms.Form, MyMethods):

    bank = forms.ModelChoiceField(queryset=Bank.objects.none(),
                                  widget=forms.widgets.Select(), label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class(PH={})
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)


class UpdateInterestForm(forms.ModelForm, MyMethods):

    class Meta:
        model = InterestRate
        fields = (
            'floating', 'fixed_1', 'fixed_2', 'fixed_3',
            'fixed_5', 'fixed_7', 'fixed_10', 'fixed_15',
            'fixed_20', 'fixed_30', 'fix_10to15', 'fix_15to20',
            'fix_20to25', 'fix_25to30', 'fix_30to35')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class(PH={})
        for field in self.fields:
            self.add_max_and_min_value(field, 25, 0)

    # 最小値と最大値のバリデーション
    def clean(self):
        super(UpdateInterestForm, self).clean()
        data = self.cleaned_data
        self.max_and_min_validation(data, 25, 0)
        return self.cleaned_data


class CreateOptionForm(forms.ModelForm, MyMethods):

    bank = forms.ModelChoiceField(
        queryset=Bank.objects.none(), widget=forms.widgets.Select(), label='銀行名')

    class Meta:
        model = Option
        fields = ('option_name', 'option_rate')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PH = {'option_name': ' 3大疾病保障特約',
              'option_rate': ' 3  (％)', }
        self.add_class(PH)
        self.add_max_and_min_value('option_rate', 25, -25)
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
        bank = data['bank'] if 'bank' in data else None
        self.same_option_validation(data, bank, selected_option=None)
        self.max_and_min_validation(data, 25, -25)
        return self.cleaned_data


class ChoiceOptionForm(forms.Form, MyMethods):

    bank = forms.ModelChoiceField(queryset=Bank.objects.none(),
                                  widget=forms.widgets.Select(attrs={
                                      'onchange': "select_option(page_type);"
                                  }), label='銀行名')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs),
        self.fields['bank'].queryset = Bank.objects.all().select_related(
            'user_id').filter(user_id__in=user)
        self.add_class(PH={})


class UpdateOptionForm(forms.ModelForm, MyMethods):

    class Meta:
        model = Option
        fields = ('option_name', 'option_rate')

    def __init__(self, selected_bank, selected_option, *args, **kwargs):
        self.selected_bank = selected_bank
        self.selected_option = selected_option
        super().__init__(*args, **kwargs)
        self.add_class(PH={})
        self.add_max_and_min_value('option_rate', 25, -25)

    def clean(self):
        super(UpdateOptionForm, self).clean()
        data = self.cleaned_data
        bank = self.selected_bank
        selected_option = self.selected_option
        self.same_option_validation(data, bank, selected_option)
        self.max_and_min_validation(data, 25, -25)
        return self.cleaned_data
