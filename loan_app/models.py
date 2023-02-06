from accounts.models import CustomUser

from django.db import models
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'my_app'


class Bank(models.Model):

    user_id = models.ForeignKey(
        CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    bank_id = models.AutoField(
        primary_key=True, unique=True, verbose_name='銀行id')
    bank_name = models.CharField(
        verbose_name='銀行名', max_length=30)

    class Meta:
        verbose_name_plural = 'Bank'

        # 1つのuserで同じ名前の銀行は1つ
        constraints = [
            models.UniqueConstraint(
                fields=["bank_name", "user_id"],
                name="bank_name_unique"
            ), ]

    def __str__(self):
        return self.bank_name


class InterestRate(models.Model):

    bank_id = models.OneToOneField(Bank, verbose_name='銀行id',
                                   on_delete=models.CASCADE, primary_key=True)
    floating = models.FloatField(verbose_name='変動金利型')
    fixed_1 = models.FloatField(verbose_name='固定金利選択型01年')
    fixed_2 = models.FloatField(verbose_name='固定金利選択型02年')
    fixed_3 = models.FloatField(verbose_name='固定金利選択型03年')
    fixed_5 = models.FloatField(verbose_name='固定金利選択型05年')
    fixed_7 = models.FloatField(verbose_name='固定金利選択型07年')
    fixed_10 = models.FloatField(verbose_name='固定金利選択型10年')
    fixed_15 = models.FloatField(verbose_name='固定金利選択型15年')
    fixed_20 = models.FloatField(verbose_name='固定金利選択型20年')
    fixed_30 = models.FloatField(verbose_name='固定金利選択型30年')
    fix_10to15 = models.FloatField(verbose_name='全期間固定金利型11〜15年')
    fix_15to20 = models.FloatField(verbose_name='全期間固定金利型16〜20年')
    fix_20to25 = models.FloatField(verbose_name='全期間固定金利型21〜25年')
    fix_25to30 = models.FloatField(verbose_name='全期間固定金利型26〜30年')
    fix_30to35 = models.FloatField(verbose_name='全期間固定金利型31〜35年')
    updated_at = models.DateField(verbose_name='更新日時', auto_now=True)

    def __str__(self):
        return str(self.bank_id)

    class Meta:
        verbose_name_plural = 'InterestRate'


class Option(models.Model):
    option_id = models.AutoField(verbose_name='オプションid', primary_key=True,
                                 unique=True,)
    bank_id = models.ForeignKey(Bank, verbose_name='銀行id',
                                on_delete=models.CASCADE)
    option_name = models.CharField(verbose_name='オプション名', max_length=30)
    option_rate = models.FloatField(verbose_name='優遇金利')
    created_at = models.DateField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateField(verbose_name='更新日時', auto_now=True)

    def __str__(self):
        return self.option_name

    class Meta:

        # 1つのUserで同じ名前の銀行は1つ
        constraints = [
            models.UniqueConstraint(
                fields=["bank_id", "option_name"],
                name="option_name_unique"
            ),
        ]

        verbose_name_plural = 'Option'
