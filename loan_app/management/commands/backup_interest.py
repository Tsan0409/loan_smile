import csv
import datetime
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Bank, InterestRate, Option

class Command(BaseCommand):
    help = 'Backup Bank Data'

    def handle(self, *args, **kwargs):

        # 実行時のYYYYMMDDを取得
        date = datetime.date.today().strftime("%Y%m%d")

        # 保存ファイルの相対パス
        file_path = settings.BACKUP_PATH + 'bank_' + date + '.csv'

        # 保存ディレクトリが存在しなければ作成
        os.makedirs(settings.BACKUP_PATH, exist_ok=True)

        # バックアップファイルの作成
        with open(file_path, 'w') as file:
            writer = csv.writer(file)

            # ヘッダーの書き込み
            bank_header = [field.name for field in Bank._meta.fields]
            writer.writerow(bank_header)

            banks = Bank.objects.all()

            for bank in banks:
                writer.writerow([str(bank.user_id),
                                 bank.bank_name,
                                 str(bank.bank_id)
                                 ])

            interest_header = [field.name for field in InterestRate._meta.fields]
            writer.writerow(interest_header)

            interests = InterestRate.objects.all()

            for interest in interests:
                writer.writerow([
                                str(interest.pk),
                                str(interest.floating),
                                str(interest.fixed_1),
                                str(interest.fixed_2),
                                str(interest.fixed_3),
                                str(interest.fixed_5),
                                str(interest.fixed_7),
                                str(interest.fixed_10),
                                str(interest.fixed_15),
                                str(interest.fixed_20),
                                str(interest.fixed_30),
                                str(interest.fix_10to15),
                                str(interest.fix_15to20),
                                str(interest.fix_20to25),
                                str(interest.fix_25to30),
                                str(interest.fix_30to35),
                                str(interest.created_at),
                                str(interest.updated_at)])

            option_header = [field.name for field in Option._meta.fields]
            writer.writerow(option_header)

            options = Option.objects.all()

            for option in options:
                writer.writerow([
                    str(option.option_id),
                    str(option.bank_id_id),
                    option.option_name,
                    str(option.option_rate),
                    str(option.created_at),
                    str(option.updated_at)])

        # 保存ディレクトリのファイルリストを取得
        files = os.listdir(settings.BACKUP_PATH)
        if len(files) >= settings.NUM_SAVED_BACKUP:
            files.sort()
            os.remove(settings.BACKUP_PATH + files[0])
