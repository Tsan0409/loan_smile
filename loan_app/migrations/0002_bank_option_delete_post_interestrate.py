# Generated by Django 4.1.3 on 2022-12-08 17:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("loan_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bank",
            fields=[
                (
                    "bank_id",
                    models.CharField(
                        max_length=8,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name="銀行id",
                    ),
                ),
                (
                    "bank_name",
                    models.CharField(max_length=30, unique=True, verbose_name="銀行名"),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="ユーザー",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Bank",},
        ),
        migrations.CreateModel(
            name="Option",
            fields=[
                (
                    "option_id",
                    models.CharField(
                        max_length=8,
                        primary_key=True,
                        serialize=False,
                        verbose_name="オプションid",
                    ),
                ),
                ("option_name", models.CharField(max_length=30, verbose_name="オプション名")),
                ("option_rate", models.FloatField(default=0, verbose_name="優遇金利")),
                ("option_ex", models.TextField(blank=True, verbose_name="説明")),
                (
                    "created_at",
                    models.DateField(auto_now_add=True, verbose_name="作成日時"),
                ),
                ("updated_at", models.DateField(auto_now=True, verbose_name="更新日時")),
                (
                    "bank_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="loan_app.bank",
                        verbose_name="銀行id",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Option",},
        ),
        migrations.DeleteModel(name="Post",),
        migrations.CreateModel(
            name="InterestRate",
            fields=[
                (
                    "bank_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="loan_app.bank",
                        verbose_name="銀行id",
                    ),
                ),
                ("floating", models.FloatField(default=0, verbose_name="")),
                ("fixed_1", models.FloatField(default=0, verbose_name="")),
                ("fixed_2", models.FloatField(default=0, verbose_name="")),
                ("fixed_3", models.FloatField(default=0, verbose_name="")),
                ("fixed_5", models.FloatField(default=0, verbose_name="")),
                ("fixed_7", models.FloatField(default=0, verbose_name="")),
                ("fixed_10", models.FloatField(default=0, verbose_name="")),
                ("fixed_15", models.FloatField(default=0, verbose_name="")),
                ("fixed_20", models.FloatField(default=0, verbose_name="")),
                ("fixed_30", models.FloatField(default=0, verbose_name="")),
                ("fix_10to15", models.FloatField(default=0, verbose_name="")),
                ("fix_15to20", models.FloatField(default=0, verbose_name="")),
                ("fix_20to25", models.FloatField(default=0, verbose_name="")),
                ("fix_25to30", models.FloatField(default=0, verbose_name="")),
                ("fix_30to35", models.FloatField(default=0, verbose_name="")),
            ],
            options={"verbose_name_plural": "InterestRate",},
        ),
    ]
