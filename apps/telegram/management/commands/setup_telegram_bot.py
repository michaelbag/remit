from django.core.management.base import BaseCommand
from django.conf import settings
from apps.telegram.bot import TelegramBot


class Command(BaseCommand):
    help = 'Setup Telegram bot webhook'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove webhook instead of setting it',
        )

    def handle(self, *args, **options):
        bot = TelegramBot()
        
        if options['remove']:
            # Удаляем webhook
            result = bot.remove_webhook()
            if result.get('ok'):
                self.stdout.write(
                    self.style.SUCCESS('Webhook successfully removed')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to remove webhook: {result}')
                )
        else:
            # Устанавливаем webhook
            result = bot.set_webhook()
            if result.get('ok'):
                self.stdout.write(
                    self.style.SUCCESS(f'Webhook successfully set to: {settings.TELEGRAM_WEBHOOK_URL}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to set webhook: {result}')
                )
            
            # Показываем информацию о webhook
            webhook_info = bot.get_webhook_info()
            if webhook_info.get('ok'):
                info = webhook_info.get('result', {})
                self.stdout.write(f'Webhook URL: {info.get("url", "Not set")}')
                self.stdout.write(f'Pending updates: {info.get("pending_update_count", 0)}')
                if info.get('last_error_message'):
                    self.stdout.write(
                        self.style.WARNING(f'Last error: {info["last_error_message"]}')
                    )
