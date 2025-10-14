from django.core.management.base import BaseCommand
from apps.telegram.models import TelegramUser
from apps.telegram.bot import TelegramBot


class Command(BaseCommand):
    help = 'Test Telegram bot commands'

    def add_arguments(self, parser):
        parser.add_argument('--chat-id', type=str, help='Telegram chat ID to send test commands to')
        parser.add_argument('--command', type=str, default='/help', help='Command to test')

    def handle(self, *args, **options):
        chat_id = options.get('chat_id')
        command = options.get('command')
        
        if not chat_id:
            self.stdout.write(
                self.style.ERROR('Please provide --chat-id argument')
            )
            return
        
        # Test command
        self.stdout.write(f'Testing command: {command}')
        bot = TelegramBot()
        
        # Check if user exists in database
        telegram_users = TelegramUser.objects.filter(telegram_id=chat_id)
        
        if telegram_users.exists():
            telegram_user = telegram_users.first()
            self.stdout.write(
                self.style.SUCCESS(f'Found Telegram user: {telegram_user.get_full_display()}')
            )
            
            # Test command handling
            try:
                from apps.telegram.models import TelegramMessage
                message = TelegramMessage.objects.create(
                    telegram_user=telegram_user,
                    message_id=9999,
                    message_type='command',
                    content=command
                )
                
                # Handle command
                response = bot.handle_command(telegram_user, command, message)
                
                if response:
                    self.stdout.write(
                        self.style.SUCCESS(f'Command handled successfully!')
                    )
                    self.stdout.write(f'Response length: {len(response)}')
                    
                    # Check if message was sent
                    message.refresh_from_db()
                    if message.is_processed and message.response:
                        self.stdout.write(
                            self.style.SUCCESS('Message was sent and saved!')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING('Message was processed but not sent')
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR('Command returned no response')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error testing command: {e}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(f'No Telegram user found with ID {chat_id} in database')
            )
        
        self.stdout.write('Test completed!')
