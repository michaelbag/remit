from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from apps.telegram.models import TelegramUser, TelegramMessage
from apps.telegram.bot import TelegramBot
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync Telegram users from recent messages and update their information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to look back for messages (default: 30)'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update information for existing users'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        days = options['days']
        update_existing = options['update_existing']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        bot = TelegramBot()
        
        # Получаем уникальных пользователей из сообщений за последние N дней
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Looking for users from messages since {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Получаем уникальные telegram_id из сообщений
        recent_telegram_ids = TelegramMessage.objects.filter(
            created_at__gte=cutoff_date
        ).values_list('telegram_user__telegram_id', flat=True).distinct()
        
        self.stdout.write(f'Found {recent_telegram_ids.count()} unique users in recent messages')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for telegram_id in recent_telegram_ids:
            try:
                # Получаем информацию о пользователе из Telegram API
                user_info = bot.get_chat_member_info(telegram_id)
                
                if not user_info:
                    self.stdout.write(
                        self.style.WARNING(f'Could not get info for user {telegram_id}')
                    )
                    error_count += 1
                    continue
                
                # Проверяем, существует ли пользователь
                try:
                    telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
                    
                    if update_existing:
                        # Обновляем существующего пользователя
                        old_username = telegram_user.username
                        old_first_name = telegram_user.first_name
                        old_last_name = telegram_user.last_name
                        
                        telegram_user.username = user_info.get('username', '')
                        telegram_user.first_name = user_info.get('first_name', '')
                        telegram_user.last_name = user_info.get('last_name', '')
                        
                        if not dry_run:
                            telegram_user.save()
                        
                        # Обновляем связанного Django пользователя
                        django_user = telegram_user.user
                        django_user.first_name = user_info.get('first_name', '')
                        django_user.last_name = user_info.get('last_name', '')
                        
                        if not dry_run:
                            django_user.save()
                        
                        updated_count += 1
                        self.stdout.write(
                            f'Updated user {telegram_id}: {old_username} -> {telegram_user.username}'
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            f'Skipped existing user {telegram_id}: {telegram_user.get_full_display()}'
                        )
                
                except TelegramUser.DoesNotExist:
                    # Создаем нового пользователя
                    if not dry_run:
                        with transaction.atomic():
                            # Создаем Django пользователя
                            django_user = User.objects.create_user(
                                username=f"telegram_{telegram_id}",
                                first_name=user_info.get('first_name', ''),
                                last_name=user_info.get('last_name', '')
                            )
                            
                            # Создаем Telegram пользователя
                            telegram_user = TelegramUser.objects.create(
                                user=django_user,
                                telegram_id=telegram_id,
                                username=user_info.get('username', ''),
                                first_name=user_info.get('first_name', ''),
                                last_name=user_info.get('last_name', '')
                            )
                    else:
                        # Для dry run создаем временный объект
                        telegram_user = type('TempUser', (), {
                            'telegram_id': telegram_id,
                            'username': user_info.get('username', ''),
                            'first_name': user_info.get('first_name', ''),
                            'last_name': user_info.get('last_name', ''),
                            'get_full_display': lambda: f"{user_info.get('first_name', '')} {user_info.get('last_name', '')} (@{user_info.get('username', '')})"
                        })()
                    
                    created_count += 1
                    self.stdout.write(
                        f'Created user {telegram_id}: {telegram_user.get_full_display()}'
                    )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing user {telegram_id}: {e}')
                )
                error_count += 1
                logger.error(f'Error syncing user {telegram_id}: {e}')
        
        # Показываем статистику
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SYNC SUMMARY:')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No actual changes made'))
        
        self.stdout.write(f'Created: {created_count} users')
        self.stdout.write(f'Updated: {updated_count} users')
        self.stdout.write(f'Skipped: {skipped_count} users')
        self.stdout.write(f'Errors: {error_count} users')
        self.stdout.write(f'Total processed: {created_count + updated_count + skipped_count + error_count} users')
        
        # Показываем общую статистику
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        
        self.stdout.write(f'\nTotal Telegram users in database: {total_users}')
        self.stdout.write(f'Active users: {active_users}')
        
        if not dry_run and (created_count > 0 or updated_count > 0):
            self.stdout.write(
                self.style.SUCCESS('\nSync completed successfully!')
            )
        elif dry_run:
            self.stdout.write(
                self.style.WARNING('\nDry run completed. Use without --dry-run to apply changes.')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\nNo changes made.')
            )
