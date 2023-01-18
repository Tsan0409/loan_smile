from django.test import LiveServerTestCase
from django.urls import reverse_lazy
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


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
#
#         self.selenium.get('http://localhost:8000' + str(reverse_lazy('account_login')))
#
#         # ログイン
#         username_input = self.selenium.find_element(By.NAME, 'login')
#         username_input.send_keys('test@gmail.com')
#         password_input = self.selenium.find_element(By.NAME, "password")
#         password_input.send_keys('aA123456789')
#         self.selenium.find_element(By.CLASS_NAME, 'btn').click()
#
#
#     def test_create_interest(self):
#         self.selenium.get(
#             'http://localhost:8000' + str(reverse_lazy('loan_app:create_interest')))
