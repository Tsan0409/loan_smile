# Generated by Django 4.1.3 on 2023-01-16 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("loan_app", "0002_alter_bank_bank_name_alter_interestrate_fixed_3"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bank",
            name="bank_name",
            field=models.CharField(max_length=30, unique=True, verbose_name="銀行名"),
        ),
    ]
