from accounts.models import CustomUser
from django.db import models


# サンプル
# class Post(models.Model):
#     title = models.CharField(max_length=255)
#     body = models.TextField()


class Bank(models.Model):
    user_id = models.ForeignKey(CustomUser, verbose_name='ユーザー',
                                on_delete=models.CASCADE)
    bank_id = models.AutoField(primary_key=True, unique=True,
                               verbose_name='銀行id')
    bank_name = models.CharField(unique=True, verbose_name='銀行名', max_length=30)

    class Meta:
        verbose_name_plural = 'Bank'

    def __str__(self):
        return self.bank_name


class InterestRate(models.Model):

    bank_id = models.OneToOneField(Bank, verbose_name='銀行id', on_delete=models.CASCADE, primary_key=True)
    floating = models.FloatField(verbose_name='変動金利型', default=0.0)
    fixed_1 = models.FloatField(verbose_name='固定金利選択型01年', default=0.0)
    fixed_2 = models.FloatField(verbose_name='固定金利選択型02年', default=0.0)
    fixed_3 = models.FloatField(verbose_name='固定金利選択型05年', default=0.0)
    fixed_5 = models.FloatField(verbose_name='固定金利選択型05年', default=0.0)
    fixed_7 = models.FloatField(verbose_name='固定金利選択型07年', default=0.0)
    fixed_10 = models.FloatField(verbose_name='固定金利選択型10年', default=0.0)
    fixed_15 = models.FloatField(verbose_name='固定金利選択型15年', default=0.0)
    fixed_20 = models.FloatField(verbose_name='固定金利選択型20年', default=0.0)
    fixed_30 = models.FloatField(verbose_name='固定金利選択型30年', default=0.0)
    fix_10to15 = models.FloatField(verbose_name='全期間固定金利型11〜15年', default=0.0)
    fix_15to20 = models.FloatField(verbose_name='全期間固定金利型16〜20年', default=0.0)
    fix_20to25 = models.FloatField(verbose_name='全期間固定金利型21〜25年', default=0.0)
    fix_25to30 = models.FloatField(verbose_name='全期間固定金利型26〜30年', default=0.0)
    fix_30to35 = models.FloatField(verbose_name='全期間固定金利型31〜35年', default=0.0)

    def __str__(self):
        return str(self.bank_id)

    class Meta:
        verbose_name_plural = 'InterestRate'


class Option(models.Model):
    option_id = models.CharField(verbose_name='オプションid', primary_key=True,
                                 max_length=8)
    bank_id = models.ForeignKey(Bank, verbose_name='銀行id',
                                on_delete=models.CASCADE)
    option_name = models.CharField(verbose_name='オプション名', max_length=30)
    option_rate = models.FloatField(verbose_name='優遇金利', default=0.0)
    option_ex = models.TextField(verbose_name='説明', blank=True)
    created_at = models.DateField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateField(verbose_name='更新日時', auto_now=True)

    def __str__(self):
        return self.option_name

    class Meta:
        verbose_name_plural = 'Option'
