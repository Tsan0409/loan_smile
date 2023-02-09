from django.contrib.auth.management.commands import createsuperuser
from loan_smile.settings_common import ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASS


class Command(createsuperuser.Command):
    help = 'Create a superuser'

    def handle(self, *args, **options):
        options.setdefault('interactive', False)
        username = ADMIN_NAME
        email = ADMIN_EMAIL
        password = ADMIN_PASS
        database = options.get('database')

        user_data = {
            'username': username,
            'email': email,
            'password': password,
        }

        # 既に同じユーザー名のユーザーが存在するか確認。なければユーザー作成
        exists = self.UserModel._default_manager.db_manager(database).filter(username=username).exists()
        if not exists:
            self.UserModel._default_manager.db_manager(database).create_superuser(**user_data)
            print('not_exist')
        else:
            print('exist')
