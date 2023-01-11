from django.apps import AppConfig


class LoanAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "loan_app"

    # def ready(self):
    #     from .scheduler.dl_loan_data import start
    #     start()
