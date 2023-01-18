# Generated by Django 4.1.3 on 2023-01-16 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("loan_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bank",
            name="bank_name",
            field=models.CharField(max_length=30, verbose_name="銀行名"),
        ),
        migrations.AlterField(
            model_name="interestrate",
            name="fixed_3",
            field=models.FloatField(default=0.0, verbose_name="固定金利選択型03年"),
        ),
    ]
