from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy
from django.test import LiveServerTestCase

from ..models import Bank, InterestRate, Option
from loan_smile.settings_common import DRIVER

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoggedInTestCase(TestCase):

    def setUp(self):
        self.password = 'aA123456789'

        self.test_user = get_user_model().objects.create_user(
            username='test',
            email='test@gmail.com',
            password=self.password
        )

        self.client.login(email=self.test_user.email, password=self.password)


class TestCreateInterestView(LoggedInTestCase):

    """CreateInterestViewテスト"""

    def test_create_interest_success(self):

        """作成処理の成功を検証"""

        params = {
            'bank_name': 'テスト銀行', 'floating': '0',
            'fixed_1': '1', 'fixed_2': '0.5', 'fixed_3': '10',
            'fixed_5': '1.5', 'fixed_7': '15', 'fixed_10': '14',
            'fixed_15': '1.545', 'fixed_20': '1.54545', 'fixed_30': '25',
            'fix_10to15': '1', 'fix_15to20': '1', 'fix_20to25': '1',
            'fix_25to30': '1', 'fix_30to35': '1',
        }

        # Post
        response = self.client.post(
            reverse_lazy('loan_app:create_interest'), params
        )

        # リダイレクトを確認
        self.assertRedirects(response, reverse_lazy('loan_app:index'))

        # データベースに登録されたかを確認する
        interest_rate = InterestRate.objects.filter(bank_id__bank_name='テスト銀行')
        self.assertEqual(Bank.objects.filter(bank_name='テスト銀行').count(), 1)
        self.assertEqual(interest_rate.count(), 1)

    def test_create_interest_failure(self):

        """テストの失敗を検証"""

        params = {
            'bank_name': 'テスト銀行', 'floating': '1',  'fixed_1': '1',
            'fixed_2': '1',  'fixed_3': '1',  'fixed_5': '1',
            'fixed_7': '1',  'fixed_10': '1',  'fixed_15': '1',
            'fixed_20': '1',  'fixed_30': '1',  'fix_10to15': '1',
            'fix_15to20': '1',  'fix_20to25': '1',  'fix_25to30': '1',
            'fix_30to35': '1',
        }

        with self.subTest('銀行名とユーザー名が一致したものが他にもある'):
            Bank.objects.create(user_id=self.test_user, bank_name='テスト銀行')
            response = self.client.post(reverse_lazy('loan_app:create_interest'), params)
            self.assertFormError(response, 'form', 'bank_name', '同じ銀行名は作成できません。')

        with self.subTest('空欄の場合'):
            response = self.value_create('loan_app:create_interest', params, '')
            self.assertFormError(response, 'form', 'bank_name', 'このフィールドは必須です。')
            for i in params:
                self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        with self.subTest('数値以外を入力した場合'):
            response = self.value_create('loan_app:create_interest', params, 'あ')
            for i in params:
                if i != 'bank_name':
                    self.assertFormError(response, 'form', i,
                                         '数値を入力してください。')

        with self.subTest('25以上を入力した場合'):
            response = self.value_create('loan_app:create_interest', params, '26')
            for i in params:
                if i != 'bank_name':
                    self.assertFormError(response, 'form', i,
                                         'この値は 25 以下でなければなりません。')
        with self.subTest('0以下を入力した場合'):
            response = self.value_create('loan_app:create_interest', params, '-1')
            for i in params:
                if i != 'bank_name':
                    self.assertFormError(response, 'form', i,
                                         'この値は 0 以上でなければなりません。')

    def value_create(self, redirect, params, value):

        for i in params:
            params[i] = value
        response = self.client.post(reverse_lazy(f'{redirect}'),
                                    params)
        return response


class TestUpdateInterestView(LoggedInTestCase):
    """Update Interest Test"""

    def test_update_interest_success(self):
        """成功を検証する"""

        # データの作成
        test_bank = Bank.objects.create(user_id=self.test_user,
                                        bank_name='テスト銀行')
        interest_rate = InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='1')

        params = {'floating': '0', 'fixed_1': '1', 'fixed_2': '0.5',
                  'fixed_3': '10', 'fixed_5': '1.5', 'fixed_7': '15',
                  'fixed_10': '14', 'fixed_15': '1.545',
                  'fixed_20': '1.54545', 'fixed_30': '1', 'fix_10to15': '1',
                  'fix_15to20': '1', 'fix_20to25': '1', 'fix_25to30': '1',
                  'fix_30to35': '1'
                  }

        response = self.client.post(reverse_lazy(
            'loan_app:update_interest', kwargs={'pk': interest_rate.pk}),
            params)

        # 作成後のリダイレクトを確認
        self.assertRedirects(response, reverse_lazy('loan_app:index'))

        # 変更したデータが一致しているかの確認
        self.assertEqual(InterestRate.objects.get(pk=interest_rate.pk).fixed_3, 10)

    def test_update_interest_failure(self):

        """失敗を検証"""

        # データの作成
        test_bank = Bank.objects.create(user_id=self.test_user,
                                        bank_name='テスト銀行')

        interest_rate = InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='1')

        params = {'floating': '', 'fixed_1': '', 'fixed_2': '',
                  'fixed_3': '', 'fixed_5': '', 'fixed_7': '',
                  'fixed_10': '', 'fixed_15': '',
                  'fixed_20': '', 'fixed_30': '', 'fix_10to15': '',
                  'fix_15to20': '', 'fix_20to25': '', 'fix_25to30': '',
                  'fix_30to35': ''
                  }

        # アカウントidが一致しない場合
        response = self.client.post(reverse_lazy(
            'loan_app:update_interest', kwargs={'pk': 999}))

        self.assertEqual(response.status_code, 404)

        # 空欄の場合の処理
        response = self.value_create(params, '', interest_rate)
        for i in params:
            self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        # 数値以外を入力した場合の処理
        response = self.value_create(params, 'あ', interest_rate)
        for i in params:
            if i != 'bank_name':
                self.assertFormError(response, 'form', i,
                                     '数値を入力してください。')

        # 25以上の数値を入力してしまった場合の処理
        response = self.value_create(params, '26', interest_rate)
        for i in params:
            self.assertFormError(response, 'form', i,
                                 'この値は 25 以下でなければなりません。')

        # 0以下の数値を入力した場合の処理
        response = self.value_create(params, '-1', interest_rate)
        for i in params:
            self.assertFormError(response, 'form', i,
                                 'この値は 0 以上でなければなりません。')

    def value_create(self, params, value, interest_rate):
        for i in params:
            params[i] = value
        response = self.client.post(reverse_lazy(
            'loan_app:update_interest', kwargs={'pk': interest_rate.pk}),
            params)
        return response


class TestInterestDeleteView(LoggedInTestCase):

    """ Delete Interest Test """

    def test_delete_interest_success(self):
        """成功を検証"""

        test_bank = Bank.objects.create(user_id=self.test_user,
                                        bank_name='テスト銀行')
        InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='1'
        )

        response = self.client.post(reverse_lazy(
            'loan_app:delete_bank', kwargs={'pk': test_bank.pk}))

        # 成功時のリダイレクトを確認
        self.assertRedirects(response, reverse_lazy('loan_app:index'))

        # 作成したデータが削除されているか確認
        self.assertEqual(Bank.objects.filter(bank_name='テスト銀行').count(), 0)
        self.assertEqual(InterestRate.objects.filter(bank_id__bank_name='テスト銀行').count(), 0)

    def test_delete_bank_failure(self):
        """失敗を検証"""

        # ユーザーが一致しない場合の処理
        response = self.client.post(
            reverse_lazy('loan_app:delete_bank', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)


class TestCreateOptionView(LoggedInTestCase):
    """ Create Option Test """

    def test_create_option_success(self):
        """成功を検証"""

        # データの作成
        Bank.objects.create(
            user_id=self.test_user, bank_name='テスト銀行')

        # パラメータの作成

        bank = Bank.objects.filter(
            bank_name='テスト銀行', user_id=self.test_user).get().bank_id

        params = {
            'option_name': 'テストオプション1', 'option_rate': '1',
            'bank': bank
        }

        # Post
        response = self.client.post(
            reverse_lazy('loan_app:create_option'), params
        )

        # リダイレクトを確認
        self.assertRedirects(response, reverse_lazy('loan_app:index'))

        # データベースに登録されたかを確認する
        option = Option.objects.filter(bank_id__bank_name='テスト銀行')
        self.assertEqual(Bank.objects.filter(bank_name='テスト銀行').count(), 1)
        self.assertEqual(option.count(), 1)

        # データベースに保存されたのが数値かどうかを確認する
        self.assertEqual(type(option.get().option_rate), float)

    def test_create_option_failure(self):

        """失敗を検証"""

        # データの作成
        bank = Bank.objects.create(
            user_id=self.test_user, bank_name='テスト銀行')

        # パラメータの作成
        bank_id = Bank.objects.filter(
            bank_name='テスト銀行', user_id=self.test_user).get().bank_id
        params = {
            'option_name': 'テストオプション', 'option_rate': '1',
            'bank': bank_id
        }

        with self.subTest('# 同じオプション名を入力した場合'):
            Option.objects.create(bank_id=bank, option_name='テストオプション', option_rate='1')
            response = self.client.post(reverse_lazy('loan_app:create_option'), params)
            self.assertFormError(
                response, 'form', 'option_name', '1つの銀行内に同じ名前のオプションは作成できません。'
            )

        with self.subTest('数値以外を入力した場合'):
            params['option_rate'] = 'あ'
            response = self.client.post(reverse_lazy('loan_app:create_option'), params)
            self.assertFormError(response, 'form', 'option_rate', '数値を入力してください。')

        with self.subTest('空欄の場合の確認'):
            response = self.value_create(params, '')
            for i in params:
                self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        with self.subTest('25以上を入力した場合'):
            params['option_rate'] = '26'
            response = self.client.post(
                reverse_lazy('loan_app:create_option'), params)
            self.assertFormError(response, 'form', 'option_rate',
                                 'この値は 25 以下でなければなりません。')

        with self.subTest('25以上を入力した場合'):
            params['option_rate'] = '-26'
            response = self.client.post(
                reverse_lazy('loan_app:create_option'), params)
            self.assertFormError(
                response, 'form', 'option_rate', 'この値は -25 以上でなければなりません。')

    def value_create(self, params, value):

        for i in params:
            params[i] = value
        response = self.client.post(
            reverse_lazy('loan_app:create_option'), params)
        return response


class TestUpdateOptionView(LoggedInTestCase):

    """ Update Option Test """

    def test_update_interest_success(self):

        """成功を検証"""

        # データの作成
        bank = Bank.objects.create(user_id=self.test_user, bank_name='テスト銀行')
        option = Option.objects.create(bank_id=bank, option_name='テストオプション',
                                       option_rate='1')

        params = {
            'option_name': 'テストオプション1', 'option_rate': '9',
            'bank': bank.bank_id}

        # Post
        response = self.client.post(
            reverse_lazy('loan_app:update_option',
                         kwargs={'pk': option.pk, 'bank_pk': bank.pk}), params)

        # リダイレクトを確認
        self.assertRedirects(response, reverse_lazy('loan_app:index'))

        # 変更したデータが一致しているかの確認
        self.assertEqual(Option.objects.get(pk=option.pk).option_rate, 9)

    def test_update_interest_failure(self):

        """失敗を検証"""

        # データの作成
        bank = Bank.objects.create(user_id=self.test_user, bank_name='テスト銀行')
        option = Option.objects.create(bank_id=bank, option_name='テストオプション',
                                       option_rate='1')

        params = {
            'option_name': 'test_option', 'option_rate': '9',
        }

        # アカウントidが一致しない場合
        response = self.client.post(reverse_lazy(
            'loan_app:update_option', kwargs={'pk': option.pk, 'bank_pk': 999}))
        self.assertEqual(response.status_code, 404)

        with self.subTest('# 同じオプション名を入力した場合'):
            Option.objects.create(bank_id=bank, option_name='test_option', option_rate='1')
            response = self.client.post(reverse_lazy(
                'loan_app:update_option', kwargs={'pk': option.pk, 'bank_pk': bank.pk}),
                params)
            self.assertFormError(
                response, 'form', 'option_name', '1つの銀行内に同じ名前のオプションは作成できません。'
            )

        with self.subTest('空欄の場合'):
            response = self.value_create(params, '', bank, option)
            for i in params:
                self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        with self.subTest('数値以外の場合'):
            response = self.value_create(params, 'あ', bank, option)
            self.assertFormError(response, 'form', 'option_rate', '数値を入力してください。')

        with self.subTest('25以上の場合'):
            response = self.value_create(params, '26', bank, option)
            self.assertFormError(response, 'form', 'option_rate',
                                 'この値は 25 以下でなければなりません。')

        with self.subTest('25以下の場合'):
            response = self.value_create(params, '-26', bank, option)
            self.assertFormError(response, 'form', 'option_rate',
                                 'この値は -25 以上でなければなりません。')

    def value_create(self, params, value, bank, option):
        for i in params:
            params[i] = value
        response = self.client.post(reverse_lazy(
            'loan_app:update_option', kwargs={'pk': option.pk, 'bank_pk': bank.pk}),
            params)
        return response


class TestOptionDeleteView(LoggedInTestCase):

    """ OPTION DELETE Test """

    def test_delete_interest_success(self):

        """成功の検証"""

        # データの作成
        bank = Bank.objects.create(user_id=self.test_user, bank_name='テスト銀行')
        option = Option.objects.create(bank_id=bank, option_name='テストオプション',
                                       option_rate='1')

        response = self.client.post(reverse_lazy(
            'loan_app:delete_option', kwargs={'pk': option.pk, 'bank_pk': bank.pk}))

        # 成功時のリダイレクトを確認
        self.assertRedirects(response, reverse_lazy('loan_app:index'))

        # 作成したデータが削除されているか確認
        self.assertEqual(Option.objects.filter(option_id=option.pk).count(), 0)

    def test_delete_bank_failure(self):

        """失敗の検証"""

        # データの作成
        bank = Bank.objects.create(user_id=self.test_user, bank_name='テスト銀行')
        option = Option.objects.create(bank_id=bank, option_name='テストオプション',
                                       option_rate='1')

        # ユーザーが一致しない場合の処理
        response = self.client.post(
            reverse_lazy('loan_app:delete_option', kwargs={'pk': option.pk, 'bank_pk': 999}))
        self.assertEqual(response.status_code, 404)


class TestBorrowableView(LiveServerTestCase, LoggedInTestCase):
    """借入可能額のテスト"""

    def test_insert_success(self):

        """成功を検証　(金利入力タイプ)"""

        test_bank = Bank.objects.create(user_id=self.test_user,
                                        bank_name='テスト銀行')

        InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='0.545')

        params = {
            'income': 600, 'repayment_ratio': 35, 'debt': 0, 'year': 35,
            'select': 0, 'interest': 0.545
        }

        with self.subTest('入力タイプ'):

            response = self.client.post(reverse_lazy(
                'loan_app:borrow_able'), params
            )
            borrow_able = response.context['borrowable']
            self.assertEqual(borrow_able, '66,921,606')

        with self.subTest('選択タイプ'):
            params['select'] = '1'
            params['bank_rate'] = 0.545
            params['bank_option'] = 0

            borrow_able = response.context['borrowable']
            self.assertEqual(borrow_able, '66,921,606')

        with self.subTest('選択タイプ（オプションあり）'):
            params['select'] = '1'
            params['bank_rate'] = 0.345
            params['bank_option'] = 0.2
            borrow_able = response.context['borrowable']
            self.assertEqual(borrow_able, '66,921,606')

    def test_borrow_able_failure(self):
        """　失敗を検証　"""

        test_bank = Bank.objects.create(user_id=self.test_user,
                                        bank_name='テスト銀行')

        InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='0.545')

        params = {
            'income': 600, 'repayment_ratio': 35, 'debt': 0, 'year': 35,
            'select': '0', 'interest': 0.545
        }

        with self.subTest('規定値をオーバーした場合'):
            response = self.value_create(params, 999999999)
            field_and_error = {'income': 'この値は 100000 以下でなければなりません。',
                               'repayment_ratio': 'この値は 40 以下でなければなりません。',
                               'debt': 'この値は 1000000 以下でなければなりません。',
                               'year': 'この値は 50 以下でなければなりません。',
                               'interest': 'この値は 25 以下でなければなりません。'}
            for field, error in field_and_error.items():
                self.assertFormError(response, 'form', field, error)

        with self.subTest('異常値を入力した場合'):
            response = self.value_create(params, -999999)
            field_and_error = {'income': 'この値は 1 以上でなければなりません。',
                               'repayment_ratio': 'この値は 1 以上でなければなりません。',
                               'debt': 'この値は 0 以上でなければなりません。',
                               'year': 'この値は 1 以上でなければなりません。',
                               'interest': 'この値は 0.0001 以上でなければなりません。'}

            for field, error in field_and_error.items():
                self.assertFormError(response, 'form', field, error)

        with self.subTest('空欄にした場合'):
            response = self.value_create(params, '')
            for i in params:
                if not i == 'select':
                    self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        with self.subTest('数値以外を入力した場合'):
            response = self.value_create(params, 'あ')
            if params['select'] == '0':
                del params['select']
                for i in params:
                    if i == 'interest':
                        self.assertFormError(response, 'form', i,
                                             '数値を入力してください。')
                    else:
                        self.assertFormError(response, 'form', i,
                                             '整数を入力してください。')

        """ SELECT BOX """

        params['select'] = 1
        params['bank'] = 1

        with self.subTest('金利がセレクトされていない場合'):
            params['bank_option'] = 1
            response = self.client.post(reverse_lazy(
                'loan_app:borrow_able'), params)
            self.assertFormError(response, 'form', 'bank', '金利が選択されていません。')

        with self.subTest('セレクトされていない場合'):
            params['bank_rate'] = 0.5
            params['bank_option'] = -0.5
            response = self.client.post(reverse_lazy(
                'loan_app:borrow_able'), params)
            self.assertFormError(response, 'form', 'bank', '金利とオプションの合計は 0 以上にしてください。')

    def value_create(self, params, value):
        for i in params:
            if not i == 'select':
                params[i] = value
        response = self.client.post(reverse_lazy(
            'loan_app:borrow_able'), params)
        return response


class TestRequiredIncomeView(LiveServerTestCase, LoggedInTestCase):
    """必要な年収の計算のテスト"""

    def test_insert_success(self):

        """成功を検証　(金利入力タイプ)"""

        test_bank = Bank.objects.create(user_id=self.test_user, bank_name='テスト銀行')
        InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='0.545')

        params = {
            'borrow': 3000, 'repayment_ratio': 35, 'year': 35,
            'select': '0', 'interest': 0.545
        }

        with self.subTest('入力タイプ'):

            response = self.client.post(reverse_lazy(
                'loan_app:required_income'), params
            )
            borrow_able = response.context['required_income']
            self.assertEqual(borrow_able, '2,689,715')

        with self.subTest('選択タイプ'):
            params['select'] = '1'
            params['bank_rate'] = 0.545
            params['bank_option'] = 0

            borrow_able = response.context['required_income']
            self.assertEqual(borrow_able, '2,689,715')

        with self.subTest('選択タイプ（オプションあり）'):
            params['select'] = '1'
            params['bank_rate'] = 0.345
            params['bank_option'] = 0.2
            borrow_able = response.context['required_income']
            self.assertEqual(borrow_able, '2,689,715')

    def test_required_income_failure(self):
        """　失敗を検証　"""

        test_bank = Bank.objects.create(user_id=self.test_user,
                                        bank_name='テスト銀行')
        InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='0.545')

        params = {
            'borrow': 3000, 'repayment_ratio': 35, 'year': 35,
            'select': '0', 'interest': 0.545
        }

        with self.subTest('規定値をオーバーした場合'):

            response = self.value_create(params, 999999999)
            field_and_error = {'borrow': 'この値は 9999999 以下でなければなりません。',
                               'repayment_ratio': 'この値は 40 以下でなければなりません。',
                               'year': 'この値は 50 以下でなければなりません。',
                               'interest': 'この値は 25 以下でなければなりません。'}

            for field, error in field_and_error.items():
                self.assertFormError(response, 'form', field, error)

        with self.subTest('異常値を入力した場合'):

            response = self.value_create(params, -999999)
            field_and_error = {'borrow': 'この値は 1 以上でなければなりません。',
                               'repayment_ratio': 'この値は 1 以上でなければなりません。',
                               'year': 'この値は 1 以上でなければなりません。',
                               'interest': 'この値は 0.0001 以上でなければなりません。'}

            for field, error in field_and_error.items():
                self.assertFormError(response, 'form', field, error)

        with self.subTest('空欄にした場合'):

            response = self.value_create(params, '')
            for i in params:
                if not i == 'select':
                    self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        with self.subTest('数値以外を入力した場合'):

            response = self.value_create(params, 'あ')
            if params['select'] == '0':
                del params['select']
                for i in params:
                    if i == 'interest':
                        self.assertFormError(response, 'form', i, '数値を入力してください。')
                    else:
                        self.assertFormError(response, 'form', i, '整数を入力してください。')

        """ SELECT BOX """

        params['select'] = '1'
        params['bank'] = 1

        with self.subTest('金利がセレクトされていない場合'):

            params['bank_option'] = 1
            response = self.client.post(reverse_lazy(
                'loan_app:required_income'), params)
            self.assertFormError(response, 'form', 'bank', '金利が選択されていません。')

        with self.subTest('セレクトされていない場合'):
            params['bank_rate'] = 0.5
            params['bank_option'] = -0.5
            response = self.client.post(
                reverse_lazy('loan_app:required_income'), params)
            self.assertFormError(response, 'form', 'bank',
                                 '金利とオプションの合計は 0 以上にしてください。')

    def value_create(self, params, value):
        for i in params:
            if not i == 'select':
                params[i] = value
        response = self.client.post(reverse_lazy(
            'loan_app:required_income'), params)
        return response


class TestRepaidView(LiveServerTestCase, LoggedInTestCase):
    """毎月の支払額をテスト"""

    def test_insert_success(self):

        """成功を検証　(金利入力タイプ)"""

        test_bank = Bank.objects.create(user_id=self.test_user,
                                        bank_name='テスト銀行')

        InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='0.545')

        params = {
            'borrow': 3000, 'year': 35, 'repaid_type': '0', 'select': '0',
            'interest': 0.545
        }

        with self.subTest('入力タイプ'):
            response = self.client.post(reverse_lazy(
                'loan_app:repaid'), params
            )
            total_repaid = response.context['total_repaid']
            amount_repaid = response.context['amount_repaid']
            interest = response.context['interest']
            self.assertEqual(total_repaid, '32,958,660')
            self.assertEqual(interest, '2,958,660')
            self.assertEqual(amount_repaid, '78,473')

        with self.subTest('選択タイプ'):
            new_params = {'select': '1', 'bank_rate': 0.545, 'bank_option': 0}
            params.update(new_params)

            total_repaid = response.context['total_repaid']
            amount_repaid = response.context['amount_repaid']
            interest = response.context['interest']
            self.assertEqual(total_repaid, '32,958,660')
            self.assertEqual(interest, '2,958,660')
            self.assertEqual(amount_repaid, '78,473')

        with self.subTest('選択タイプ（オプションあり）'):
            new_params = {'select': '1', 'bank_rate': 0.345, 'bank_option': 2}
            params.update(new_params)

            total_repaid = response.context['total_repaid']
            amount_repaid = response.context['amount_repaid']
            interest = response.context['interest']
            self.assertEqual(total_repaid, '32,958,660')
            self.assertEqual(interest, '2,958,660')
            self.assertEqual(amount_repaid, '78,473')

    def test_repaid_failure(self):
        """　失敗を検証　"""

        test_bank = Bank.objects.create(user_id=self.test_user,
                                        bank_name='テスト銀行')

        InterestRate.objects.create(
            bank_id=test_bank, floating='1', fixed_1='1',
            fixed_2='1', fixed_3='1', fixed_5='1', fixed_7='1',
            fixed_10='1', fixed_15='1', fixed_20='1', fixed_30='1',
            fix_10to15='1', fix_15to20='1', fix_20to25='1',
            fix_25to30='1', fix_30to35='0.545')

        params = {
            'borrow': 3000, 'year': 35, 'repaid_type': '0', 'select': '0',
            'interest': 0.545
        }

        with self.subTest('規定値をオーバーした場合'):

            response = self.value_create(params, 999999999)
            field_and_error = {'borrow': 'この値は 9999999 以下でなければなりません。',
                               'year': 'この値は 50 以下でなければなりません。',
                               'interest': 'この値は 25 以下でなければなりません。'}

            for field, error in field_and_error.items():
                self.assertFormError(response, 'form', field, error)

        with self.subTest('異常値を入力した場合'):

            response = self.value_create(params, -9999999)
            field_and_error = {'borrow': 'この値は 1 以上でなければなりません。',
                               'year': 'この値は 1 以上でなければなりません。',
                               'interest': 'この値は 0.0001 以上でなければなりません。'}

            for field, error in field_and_error.items():
                self.assertFormError(response, 'form', field, error)

        with self.subTest('空欄にした場合'):

            response = self.value_create(params, '')
            for i in params:
                if i != 'select' and i != 'repaid_type':
                    self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        with self.subTest('数値以外を入力した場合'):

            response = self.value_create(params, 'あ')
            if params['select'] == '0':
                del params['select'], params['repaid_type']
                for i in params:
                    if i == 'interest':
                        self.assertFormError(response, 'form', i,
                                             '数値を入力してください。')
                    else:
                        self.assertFormError(response, 'form', i,
                                             '整数を入力してください。')

        """ SELECT BOX """

        new_params = {'select': '1', 'bank': 1}
        params.update(new_params)

        with self.subTest('金利がセレクトされていない場合'):
            params['bank_option'] = 1
            response = self.client.post(reverse_lazy(
                'loan_app:repaid'), params)
            self.assertFormError(response, 'form', 'bank', '金利が選択されていません。')

        with self.subTest('セレクトされていない場合'):
            params['bank_rate'] = 2
            params['bank_option'] = -2
            response = self.client.post(
                reverse_lazy('loan_app:repaid'), params)
            self.assertFormError(response, 'form', 'bank',
                                 '金利とオプションの合計は 0 以上にしてください。')

    def value_create(self, params, value):
        for i in params:
            if not i == 'select':
                params[i] = value
        response = self.client.post(reverse_lazy(
            'loan_app:repaid'), params)
        return response


def next_url_fact(reverse, next_page):
    url = f'http://localhost:8000{reverse_lazy(reverse)}?next={reverse_lazy(next_page)}'
    return url


def url_fact(reverse):
    url = f'http://localhost:8000{reverse_lazy(reverse)}'
    return url


class TestRedirectLogin(LiveServerTestCase):
    """　ログイン専用のページにアクセスしているか確認　"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opt = ChromeOptions()
        opt.add_argument('--headless')
        cls.selenium = WebDriver(executable_path=DRIVER, options=opt)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get('http://localhost:8000' + str(reverse_lazy('account_login')))
        # ログイン
        username_input = self.selenium.find_element(By.NAME, 'login')
        username_input.send_keys('test@gmail.com')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('aA123456789')
        self.selenium.find_element(By.CLASS_NAME, 'btn').click()

    # クリック先のURL取得
    def click_and_get(self, html_name):
        self.selenium.get('http://localhost:8000')
        self.selenium.find_element(By.NAME, html_name).click()
        cur_url = self.selenium.current_url
        return cur_url

    # ハンバーガーメニュー
    def click_and_get_Ha(self, html_name, header):
        self.selenium.get('http://localhost:8000')
        self.selenium.find_element(By.XPATH, '//*[@id="open_nav"]/img').click()
        WebDriverWait(self.selenium, 2).until(EC.element_to_be_clickable(
            (By.ID, header))).click()
        WebDriverWait(self.selenium, 2).until(EC.element_to_be_clickable(
            (By.NAME, html_name))).click()
        cur_url = self.selenium.current_url
        return cur_url

    # サイドメニュー
    def click_and_get_Sub(self, html_name, header):
        self.selenium.get('http://localhost:8000')
        WebDriverWait(self.selenium, 2).until(EC.element_to_be_clickable(
            (By.ID, header))).click()
        WebDriverWait(self.selenium, 2).until(EC.element_to_be_clickable(
            (By.NAME, html_name))).click()
        cur_url = self.selenium.current_url
        return cur_url

    def test_index_redirect(self):
        """ ホームページからのリダイレクトをテスト　"""

        self.test_login()

        with self.subTest('BorrowAble'):
            self.assertEqual(self.click_and_get("index_borrow_able"),
                             url_fact('loan_app:borrow_able'))

        with self.subTest('required_income'):
            self.assertEqual(self.click_and_get("index_required_income"),
                             url_fact('loan_app:required_income'))

        with self.subTest('Repaid'):
            self.assertEqual(self.click_and_get("index_repaid"),
                             url_fact('loan_app:repaid'))

        with self.subTest('CompareInterest'):
            self.assertEqual(self.click_and_get("index_compare_interest"),
                             url_fact('loan_app:compare_interest'))

        with self.subTest('CreateInterest'):
            self.assertEqual(self.click_and_get("index_create_interest"),
                             url_fact('loan_app:create_interest'))

        with self.subTest('ChoiceBank'):
            self.assertEqual(self.click_and_get("index_choice_bank"),
                             url_fact('loan_app:choice_bank'))

        with self.subTest('CreateOption'):
            self.assertEqual(self.click_and_get("index_create_option"),
                             url_fact('loan_app:create_option'))

        with self.subTest('ChoiceOption'):
            self.assertEqual(self.click_and_get("index_choice_option"),
                             url_fact('loan_app:choice_option'))

        with self.subTest('Signup'):
            self.assertEqual(self.click_and_get("index_signup"),
                             url_fact('loan_app:index'))

        with self.subTest('Login'):
            self.assertEqual(self.click_and_get("index_login"),
                             url_fact('loan_app:index'))

        with self.subTest('Logout'):
            self.assertEqual(self.click_and_get("index_logout"),
                             url_fact('loan_app:index'))

    def test_side_redirect(self):
        """ サイドメニューからのリダイレクトをテスト　"""

        self.selenium.get('http://localhost:8000')
        self.selenium.set_window_size(1024, 840)

        with self.subTest('Inquiry'):
            self.assertEqual(self.click_and_get("side_inquiry"),
                             url_fact('loan_app:inquiry'))

        with self.subTest('BorrowAble'):
            self.assertEqual(self.click_and_get_Sub("side_borrow_able", 'sub_calc'),
                             url_fact('loan_app:borrow_able'))

        with self.subTest('required_income'):
            self.assertEqual(self.click_and_get_Sub("side_required_income", 'sub_calc'),
                             url_fact('loan_app:required_income'))

        with self.subTest('Repaid'):
            self.assertEqual(self.click_and_get_Sub("side_repaid", 'sub_calc'),
                             url_fact('loan_app:repaid'))

        with self.subTest('CompareInterest'):
            self.assertEqual(self.click_and_get_Sub("side_compare_interest", 'sub_bank'),
                             url_fact('loan_app:compare_interest'))

        with self.subTest('CreateInterest'):
            self.assertEqual(self.click_and_get_Sub("side_create_interest", 'sub_bank'),
                             url_fact('loan_app:create_interest'))

        with self.subTest('ChoiceBank'):
            self.assertEqual(self.click_and_get_Sub("side_choice_bank", 'sub_bank'),
                             url_fact('loan_app:choice_bank'))

        with self.subTest('CreateOption'):
            self.assertEqual(self.click_and_get_Sub("side_create_option", 'sub_bank'),
                             url_fact('loan_app:create_option'))

        with self.subTest('ChoiceOption'):
            self.assertEqual(self.click_and_get_Sub("side_choice_option", 'sub_bank'),
                             url_fact('loan_app:choice_option'))

        with self.subTest('Signup'):
            self.assertEqual(self.click_and_get_Sub("side_signup", 'sub_account'),
                             url_fact('loan_app:index'))

        with self.subTest('Login'):
            self.assertEqual(self.click_and_get_Sub("side_login", 'sub_account'),
                             url_fact('loan_app:index'))

        with self.subTest('Logout'):
            self.assertEqual(self.click_and_get_Sub("side_logout", 'sub_account'),
                             url_fact('loan_app:index'))

    def test_hamburger_redirect(self):
        """ ハンバーガーメニューからのリダイレクトをテスト　"""

        self.test_login()
        self.selenium.get('http://localhost:8000')
        self.selenium.set_window_size(390, 840)

        with self.subTest('Inquiry'):
            self.selenium.get('http://localhost:8000')
            self.selenium.find_element(By.XPATH, '//*[@id="open_nav"]/img').click()
            WebDriverWait(self.selenium, 2).until(
                EC.element_to_be_clickable((By.ID, 'hidden_inquiry'))).click()
            cur_url = self.selenium.current_url
            self.assertEqual(cur_url, url_fact('loan_app:inquiry'))

        with self.subTest('BorrowAble'):
            self.assertEqual(self.click_and_get_Ha("hamburger_borrow_able", 'hidden_calc'),
                             url_fact('loan_app:borrow_able'))

        with self.subTest('required_income'):
            self.assertEqual(self.click_and_get_Ha("hamburger_required_income", 'hidden_calc'),
                             url_fact('loan_app:required_income'))

        with self.subTest('Repaid'):
            self.assertEqual(self.click_and_get_Ha("hamburger_repaid", 'hidden_calc'),
                             url_fact('loan_app:repaid'))

        with self.subTest('CompareInterest'):
            self.assertEqual(self.click_and_get_Ha("hamburger_compare_interest", 'hidden_bank'),
                             url_fact('loan_app:compare_interest'))

        with self.subTest('CreateInterest'):
            self.assertEqual(self.click_and_get_Ha("hamburger_create_interest", 'hidden_bank'),
                             url_fact('loan_app:create_interest'))

        with self.subTest('ChoiceBank'):
            self.assertEqual(self.click_and_get_Ha("hamburger_choice_bank", 'hidden_bank'),
                             url_fact('loan_app:choice_bank'))

        with self.subTest('CreateOption'):
            self.assertEqual(self.click_and_get_Ha("hamburger_create_option",'hidden_bank'),
                             url_fact('loan_app:create_option'))

        with self.subTest('ChoiceOption'):
            self.assertEqual(self.click_and_get_Ha("hamburger_choice_option",'hidden_bank'),
                             url_fact('loan_app:choice_option'))

        with self.subTest('Signup'):
            self.assertEqual(self.click_and_get_Ha("hamburger_signup", 'hidden_account'),
                             url_fact('loan_app:index'))

        with self.subTest('Login'):
            self.assertEqual(self.click_and_get_Ha("hamburger_login", 'hidden_account'),
                             url_fact('loan_app:index'))

        with self.subTest('Logout'):
            self.assertEqual(self.click_and_get_Ha("hamburger_logout", 'hidden_account'),
                             url_fact('loan_app:index'))


class TestRedirectLogout(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opt = ChromeOptions()
        opt.add_argument('--headless')
        cls.selenium = WebDriver(executable_path=DRIVER, options=opt)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    # クリック先のURL取得
    def click_and_get(self, html_name):
        self.selenium.get('http://localhost:8000')
        self.selenium.find_element(By.NAME, html_name).click()
        cur_url = self.selenium.current_url
        return cur_url

    def click_and_get_Ha(self, html_name, header):
        self.selenium.get('http://localhost:8000')
        self.selenium.find_element(By.XPATH, '//*[@id="open_nav"]/img').click()
        WebDriverWait(self.selenium, 2).until(EC.element_to_be_clickable(
            (By.ID, header))).click()
        WebDriverWait(self.selenium, 2).until(EC.element_to_be_clickable(
            (By.NAME, html_name))).click()
        cur_url = self.selenium.current_url
        return cur_url

    def click_and_get_Sub(self, html_name, header):
        self.selenium.get('http://localhost:8000')
        WebDriverWait(self.selenium, 2).until(EC.element_to_be_clickable(
            (By.ID, header))).click()
        WebDriverWait(self.selenium, 2).until(EC.element_to_be_clickable(
            (By.NAME, html_name))).click()
        cur_url = self.selenium.current_url
        return cur_url

    def test_index_redirect(self):
        """ ホームページからのリダイレクトをテスト　"""

        with self.subTest('BorrowAble'):
            self.assertEqual(self.click_and_get("index_borrow_able"),
                             url_fact('loan_app:borrow_able'))

        with self.subTest('required_income'):
            self.assertEqual(self.click_and_get("index_required_income"),
                             url_fact('loan_app:required_income'))

        with self.subTest('Repaid'):
            self.assertEqual(self.click_and_get("index_repaid"),
                             url_fact('loan_app:repaid'))

        with self.subTest('CompareInterest'):
            self.assertEqual(self.click_and_get("index_compare_interest"),
                             url_fact('loan_app:compare_interest'))

        with self.subTest('CreateInterest'):
            self.assertEqual(self.click_and_get("index_create_interest"),
                             next_url_fact('account_login', 'loan_app:create_interest'))

        with self.subTest('ChoiceBank'):
            self.assertEqual(self.click_and_get("index_choice_bank"),
                             next_url_fact('account_login', 'loan_app:choice_bank'))

        with self.subTest('CreateOption'):
            self.assertEqual(self.click_and_get("index_create_option"),
                             next_url_fact('account_login', 'loan_app:create_option'))

        with self.subTest('ChoiceOption'):
            self.assertEqual(self.click_and_get("index_choice_option"),
                             next_url_fact('account_login', 'loan_app:choice_option'))

        with self.subTest('Signup'):
            self.assertEqual(self.click_and_get("index_signup"),
                             url_fact('account_signup'))

        with self.subTest('Login'):
            self.assertEqual(self.click_and_get("index_login"),
                             url_fact('account_login'))

        with self.subTest('Logout'):
            self.assertEqual(self.click_and_get("index_logout"),
                             url_fact('loan_app:index'))


    def test_side_redirect(self):
        """ サイドメニューからのリダイレクトをテスト　"""

        self.selenium.get('http://localhost:8000')
        self.selenium.set_window_size(1024, 840)

        with self.subTest('Inquiry'):
            self.assertEqual(self.click_and_get("side_inquiry"),
                             url_fact('loan_app:inquiry'))

        with self.subTest('BorrowAble'):
            self.assertEqual(self.click_and_get_Sub("side_borrow_able", 'sub_calc'),
                             url_fact('loan_app:borrow_able'))

        with self.subTest('required_income'):
            self.assertEqual(self.click_and_get_Sub("side_required_income", 'sub_calc'),
                             url_fact('loan_app:required_income'))

        with self.subTest('Repaid'):
            self.assertEqual(self.click_and_get_Sub("side_repaid", 'sub_calc'),
                             url_fact('loan_app:repaid'))

        with self.subTest('CompareInterest'):
            self.assertEqual(self.click_and_get_Sub("side_compare_interest", 'sub_bank'),
                             url_fact('loan_app:compare_interest'))

        with self.subTest('CreateInterest'):
            self.assertEqual(self.click_and_get_Sub("side_create_interest", 'sub_bank'),
                             next_url_fact('account_login', 'loan_app:create_interest'))

        with self.subTest('ChoiceBank'):
            self.assertEqual(self.click_and_get_Sub("side_choice_bank", 'sub_bank'),
                             next_url_fact('account_login', 'loan_app:choice_bank'))

        with self.subTest('CreateOption'):
            self.assertEqual(self.click_and_get_Sub("side_create_option", 'sub_bank'),
                             next_url_fact('account_login', 'loan_app:create_option'))

        with self.subTest('ChoiceOption'):
            self.assertEqual(self.click_and_get_Sub("side_choice_option", 'sub_bank'),
                             next_url_fact('account_login', 'loan_app:choice_option'))

        with self.subTest('Signup'):
            self.assertEqual(self.click_and_get_Sub("side_signup", 'sub_account'),
                             url_fact('account_signup'))

        with self.subTest('Login'):
            self.assertEqual(self.click_and_get_Sub("side_login", 'sub_account'),
                             url_fact('account_login'))

        with self.subTest('Logout'):
            self.assertEqual(self.click_and_get_Sub("side_logout", 'sub_account'),
                             url_fact('loan_app:index'))

    def test_hamburger_redirect(self):
        """ ハンバーガーメニューからのリダイレクトをテスト　"""

        self.selenium.get('http://localhost:8000')
        self.selenium.set_window_size(390, 840)

        with self.subTest('BorrowAble'):
            self.assertEqual(self.click_and_get("index_borrow_able"),
                             url_fact('loan_app:borrow_able'))

        with self.subTest('required_income'):
            self.assertEqual(self.click_and_get("index_required_income"),
                             url_fact('loan_app:required_income'))

        with self.subTest('Repaid'):
            self.assertEqual(self.click_and_get("index_repaid"),
                             url_fact('loan_app:repaid'))

        with self.subTest('CompareInterest'):
            self.assertEqual(self.click_and_get("index_compare_interest"),
                             url_fact('loan_app:compare_interest'))

        with self.subTest('CreateInterest'):
            self.assertEqual(self.click_and_get_Ha("hamburger_create_interest", 'hidden_bank'),
                             next_url_fact('account_login', 'loan_app:create_interest'))

        with self.subTest('ChoiceBank'):
            self.assertEqual(self.click_and_get_Ha("hamburger_choice_bank", 'hidden_bank'),
                             next_url_fact('account_login', 'loan_app:choice_bank'))

        with self.subTest('CreateOption'):
            self.assertEqual(self.click_and_get_Ha("hamburger_create_option",'hidden_bank'),
                             next_url_fact('account_login', 'loan_app:create_option'))

        with self.subTest('ChoiceOption'):
            self.assertEqual(self.click_and_get_Ha("hamburger_choice_option",'hidden_bank'),
                             next_url_fact('account_login', 'loan_app:choice_option'))

        with self.subTest('Signup'):
            self.assertEqual(self.click_and_get_Ha("hamburger_signup", 'hidden_account'),
                             url_fact('account_signup'))

        with self.subTest('Login'):
            self.assertEqual(self.click_and_get_Ha("hamburger_login", 'hidden_account'),
                             url_fact('account_login'))

        with self.subTest('Logout'):
            self.assertEqual(self.click_and_get_Ha("hamburger_logout", 'hidden_account'),
                             url_fact('loan_app:index'))
