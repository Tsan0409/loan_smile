from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

from ..models import Bank, InterestRate, Option

from django.test import LiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


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

        # データベースに保存されたのが数値かどうかを確認する
        self.assertEqual(type(interest_rate.get().floating), float)

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

        # 同じ銀行名を入力した場合
        with self.subTest('銀行名とユーザー名が一致したものが他にもある'):
            Bank.objects.create(user_id=self.test_user, bank_name='テスト銀行')
            response = self.client.post(reverse_lazy('loan_app:create_interest'), params)
            self.assertFormError(response, 'form', 'bank_name', '同じ銀行名は作成できません。')

        # 空欄の場合の確認
        response = self.value_create('loan_app:create_interest', params, '')
        self.assertFormError(response, 'form', 'bank_name', 'このフィールドは必須です。')
        for i in params:
            self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        # 数値以外を入力した場合
        response = self.value_create('loan_app:create_interest', params, 'あ')
        for i in params:
            if i != 'bank_name':
                self.assertFormError(response, 'form', i,
                                     '数値を入力してください。')

        # 25以上を入力した場合
        response = self.value_create('loan_app:create_interest', params, '26')
        for i in params:
            if i != 'bank_name':
                self.assertFormError(response, 'form', i,
                                     'この値は 25 以下でなければなりません。')

        # 0以下を入力した場合
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

    def test_update_interest_success(self):
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
        """アップデートの失敗を検証"""

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

    def test_delete_interest_success(self):
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

        # ユーザーが一致しない場合の処理
        response = self.client.post(
            reverse_lazy('loan_app:delete_bank', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)


class TestCreateOptionView(LoggedInTestCase):
    """CreateOptionViewテスト"""

    def test_create_option_success(self):
        """作成処理の成功を検証"""

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
        """テストの失敗を検証"""

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

        # 同じオプション名を入力した場合
        with self.subTest('# 同じオプション名を入力した場合'):
            Option.objects.create(bank_id=bank, option_name='テストオプション', option_rate='1')
            response = self.client.post(reverse_lazy('loan_app:create_option'), params)
            self.assertFormError(
                response, 'form', 'option_name', '1つの銀行内に同じ名前のオプションは作成できません。'
            )

        # 数値以外を入力した場合
        with self.subTest('数値以外を入力した場合'):
            params['option_rate'] = 'あ'
            response = self.client.post(reverse_lazy('loan_app:create_option'), params)
            self.assertFormError(response, 'form', 'option_rate', '数値を入力してください。')

        # 空欄の場合の確認
        with self.subTest('空欄の場合の確認'):
            response = self.value_create(params, '')
            for i in params:
                self.assertFormError(response, 'form', i, 'このフィールドは必須です。')

        # 25以上を入力した場合
        with self.subTest('25以上を入力した場合'):
            params['option_rate'] = '26'
            response = self.client.post(
                reverse_lazy('loan_app:create_option'), params)
            self.assertFormError(response, 'form', 'option_rate',
                                 'この値は 25 以下でなければなりません。')

        # 25以上を入力した場合
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
    """TestUpdateOptionViewのテスト"""

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
        """アップデートの失敗を検証"""

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
    """ TEST OPTION DELETE """

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


# ログアウト後のURL先の確認
# class TestLogin(LiveServerTestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.selenium = WebDriver(executable_path='/Users/tsukakosuke/Desktop/chromedriver_mac64 /chromedriver')
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super().tearDownClass()
#
#     def test_login(self):
#         print('login')
#
#         self.selenium.get('http://localhost:8000' + str(reverse_lazy('account_login')))
#
#         # ログイン
#         username_input = self.selenium.find_element(By.NAME, 'login')
#         username_input.send_keys('test@gmail.com')
#         password_input = self.selenium.find_element(By.NAME, "password")
#         password_input.send_keys('aA123456789')
#         self.selenium.find_element(By.CLASS_NAME, 'btn').click()


# class TestBorrowableView(LiveServerTestCase):
#     """借入可能額のテスト"""
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.selenium = WebDriver(
#             executable_path='/Users/tsukakosuke/Desktop/chromedriver_mac64 /chromedriver')
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super().tearDownClass()
#
#     # ログイン
#     def login_func(self):
#         print('login_func')
#         username_input = self.selenium.find_element(By.NAME, 'login')
#         username_input.send_keys('test@gmail.com')
#         password_input = self.selenium.find_element(By.NAME, "password")
#         password_input.send_keys('aA123456789')
#         self.selenium.find_element(By.CLASS_NAME, 'btn').click()
#
#     def test_insert_success(self):
#         self.selenium.get(
#             'http://localhost:8000' + str(reverse_lazy('loan_app:borrow_able')))
#
#         income = self.selenium.find_element(By.NAME, 'income')
#         income.send_keys(400)
#         repayment_ratio = self.selenium.find_element(By.NAME, 'repayment_ratio')
#         repayment_ratio.send_keys(35)
#         debt = self.selenium.find_element(By.NAME, 'debt')
#         debt.send_keys(0)
#         year = self.selenium.find_element(By.NAME, 'year')
#         year.send_keys(35)
#         interest = self.selenium.find_element(By.NAME, 'interest')
#         interest.send_keys(0.545)
#
#         self.selenium.find_element(By.CLASS_NAME, 'btn').click()
#         print('finished test insert ')
#
#     def test_select_success(self):
#         self.selenium.get(
#             'http://localhost:8000' + str(reverse_lazy('loan_app:borrow_able')))
#
#         income = self.selenium.find_element(By.NAME, 'income')
#         income.send_keys(400)
#         repayment_ratio = self.selenium.find_element(By.NAME, 'repayment_ratio')
#         repayment_ratio.send_keys(35)
#         debt = self.selenium.find_element(By.NAME, 'debt')
#         debt.send_keys(0)
#         year = self.selenium.find_element(By.NAME, 'year')
#         year.send_keys(35)
#         self.selenium.find_elements(By.NAME, 'select')[1].click()
#         bank_id = self.selenium.find_element(By.NAME, 'bank')
#         select_id = Select(bank_id)
#         select_id.select_by_index(len(select_id.options) - 1)
#         interest = self.selenium.find_element(By.NAME, 'bank_rate')
#         select_interest = Select(interest)
#         select_interest.select_by_index(len(select_interest.options) - 1)
#
#         self.selenium.find_element(By.CLASS_NAME, 'btn').click()
#         print('finished test selected')

    # 異常値を入力した場合

    # 数値以外を入力した場合

    # 属性の選択

    # セレクトボックスから数値を得ているかの確認

    # 金利の required　が外れているのか

    # セレクトボックスrequiredが外れているのか

    # データの個数が　デフォルト　＋　ユーザー分かどうか

    # 入力した後セレクトボックスの一つ目が同じ数値か
