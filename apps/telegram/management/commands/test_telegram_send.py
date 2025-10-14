from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.telegram.models import TelegramUser, TelegramBroadcast, TelegramSubscriptionCategory
from apps.telegram.services import TelegramBroadcastService
from apps.telegram.bot import TelegramBot


class Command(BaseCommand):
    help = 'Test Telegram message sending'

    def add_arguments(self, parser):
        parser.add_argument('--chat-id', type=str, help='Telegram chat ID to send test message to')
        parser.add_argument('--message', type=str, default='Test message from Django', help='Message to send')

    def handle(self, *args, **options):
        chat_id = options.get('chat_id')
        message = options.get('message')
        
        if not chat_id:
            self.stdout.write(
                self.style.ERROR('Please provide --chat-id argument')
            )
            return
        
        # Test 1: Direct bot message
        self.stdout.write('Testing direct bot message...')
        bot = TelegramBot()
        response = bot.send_message(chat_id, message)
        
        if response and response.get('ok'):
            self.stdout.write(
                self.style.SUCCESS(f'Direct message sent successfully! Message ID: {response.get("result", {}).get("message_id")}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to send direct message: {response}')
            )
        
        # Test 2: Check if user exists in database
        self.stdout.write('Checking Telegram users in database...')
        telegram_users = TelegramUser.objects.filter(telegram_id=chat_id)
        
        if telegram_users.exists():
            telegram_user = telegram_users.first()
            self.stdout.write(
                self.style.SUCCESS(f'Found Telegram user: {telegram_user.get_full_display()}')
            )
            
            # Test 3: Create test broadcast
            self.stdout.write('Creating test broadcast...')
            try:
                # Get or create a test category
                category, created = TelegramSubscriptionCategory.objects.get_or_create(
                    code='test',
                    defaults={
                        'name': 'Test Category',
                        'description': 'Test category for testing broadcasts',
                        'is_active': True,
                        'is_public': True,
                        'requires_approval': False
                    }
                )
                
                if created:
                    self.stdout.write(f'Created test category: {category.name}')
                else:
                    self.stdout.write(f'Using existing category: {category.name}')
                
                # Create broadcast
                broadcast_service = TelegramBroadcastService()
                broadcast = broadcast_service.create_broadcast(
                    title='Test Broadcast',
                    message=f'Test broadcast message: {message}',
                    target_users=[telegram_user],
                    created_by=User.objects.first()
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created broadcast: {broadcast.title} (ID: {broadcast.id})')
                )
                
                # Test 4: Send broadcast
                self.stdout.write('Sending broadcast...')
                result = broadcast_service.send_broadcast(broadcast.id)
                
                if result:
                    self.stdout.write(
                        self.style.SUCCESS('Broadcast sent successfully!')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Failed to send broadcast!')
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating/sending broadcast: {e}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(f'No Telegram user found with ID {chat_id} in database')
            )
            self.stdout.write('You can create a user manually in Django admin or through the bot')
        
        self.stdout.write('Test completed!')
