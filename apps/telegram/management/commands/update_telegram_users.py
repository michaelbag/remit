from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from apps.telegram.models import TelegramUser, TelegramMessage
from apps.telegram.bot import TelegramBot
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update Telegram users information from all available sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Update all existing Telegram users'
        )
        parser.add_argument(
            '--from-messages',
            action='store_true',
            help='Update users from message history'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days to look back for messages (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        all_users = options['all_users']
        from_messages = options['from_messages']
        days = options['days']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        bot = TelegramBot()
        
        updated_count = 0
        error_count = 0
        skipped_count = 0
        
        if all_users:
            # Обновляем всех существующих пользователей
            self.stdout.write('Updating all existing Telegram users...')
            telegram_users = TelegramUser.objects.all()
            
            for telegram_user in telegram_users:
                try:
                    user_info = bot.get_chat_member_info(telegram_user.telegram_id)
                    
                    if not user_info:
                        self.stdout.write(
                            self.style.WARNING(f'Could not get info for user {telegram_user.telegram_id}')
                        )
                        error_count += 1
                        continue
                    
                    # Проверяем, изменились ли данные
                    old_username = telegram_user.username
                    old_first_name = telegram_user.first_name
                    old_last_name = telegram_user.last_name
                    
                    new_username = user_info.get('username', '')
                    new_first_name = user_info.get('first_name', '')
                    new_last_name = user_info.get('last_name', '')
                    
                    if (old_username != new_username or 
                        old_first_name != new_first_name or 
                        old_last_name != new_last_name):
                        
                        if not dry_run:
                            telegram_user.username = new_username
                            telegram_user.first_name = new_first_name
                            telegram_user.last_name = new_last_name
                            telegram_user.save()
                            
                            # Обновляем связанного Django пользователя
                            django_user = telegram_user.user
                            django_user.first_name = new_first_name
                            django_user.last_name = new_last_name
                            django_user.save()
                        
                        updated_count += 1
                        self.stdout.write(
                            f'Updated user {telegram_user.telegram_id}: '
                            f'{old_username} -> {new_username}, '
                            f'{old_first_name} {old_last_name} -> {new_first_name} {new_last_name}'
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            f'No changes for user {telegram_user.telegram_id}: {telegram_user.get_full_display()}'
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error updating user {telegram_user.telegram_id}: {e}')
                    )
                    error_count += 1
                    logger.error(f'Error updating user {telegram_user.telegram_id}: {e}')
        
        elif from_messages:
            # Обновляем пользователей из сообщений
            from django.utils import timezone
            from datetime import timedelta
            
            cutoff_date = timezone.now() - timedelta(days=days)
            
            self.stdout.write(f'Updating users from messages since {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}')
            
            # Получаем уникальные telegram_id из сообщений
            recent_telegram_ids = TelegramMessage.objects.filter(
                created_at__gte=cutoff_date
            ).values_list('telegram_user__telegram_id', flat=True).distinct()
            
            self.stdout.write(f'Found {recent_telegram_ids.count()} unique users in recent messages')
            
            for telegram_id in recent_telegram_ids:
                try:
                    user_info = bot.get_chat_member_info(telegram_id)
                    
                    if not user_info:
                        self.stdout.write(
                            self.style.WARNING(f'Could not get info for user {telegram_id}')
                        )
                        error_count += 1
                        continue
                    
                    try:
                        telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
                        
                        # Проверяем, изменились ли данные
                        old_username = telegram_user.username
                        old_first_name = telegram_user.first_name
                        old_last_name = telegram_user.last_name
                        
                        new_username = user_info.get('username', '')
                        new_first_name = user_info.get('first_name', '')
                        new_last_name = user_info.get('last_name', '')
                        
                        if (old_username != new_username or 
                            old_first_name != new_first_name or 
                            old_last_name != new_last_name):
                            
                            if not dry_run:
                                telegram_user.username = new_username
                                telegram_user.first_name = new_first_name
                                telegram_user.last_name = new_last_name
                                telegram_user.save()
                                
                                # Обновляем связанного Django пользователя
                                django_user = telegram_user.user
                                django_user.first_name = new_first_name
                                django_user.last_name = new_last_name
                                django_user.save()
                            
                            updated_count += 1
                            self.stdout.write(
                                f'Updated user {telegram_id}: '
                                f'{old_username} -> {new_username}, '
                                f'{old_first_name} {old_last_name} -> {new_first_name} {new_last_name}'
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                f'No changes for user {telegram_id}: {telegram_user.get_full_display()}'
                            )
                    
                    except TelegramUser.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'User {telegram_id} not found in database')
                        )
                        skipped_count += 1
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing user {telegram_id}: {e}')
                    )
                    error_count += 1
                    logger.error(f'Error processing user {telegram_id}: {e}')
        
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --all-users or --from-messages')
            )
            return
        
        # Показываем статистику
        self.stdout.write('\n' + '='*50)
        self.stdout.write('UPDATE SUMMARY:')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No actual changes made'))
        
        self.stdout.write(f'Updated: {updated_count} users')
        self.stdout.write(f'Skipped: {skipped_count} users')
        self.stdout.write(f'Errors: {error_count} users')
        self.stdout.write(f'Total processed: {updated_count + skipped_count + error_count} users')
        
        # Показываем общую статистику
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        
        self.stdout.write(f'\nTotal Telegram users in database: {total_users}')
        self.stdout.write(f'Active users: {active_users}')
        
        if not dry_run and updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS('\nUpdate completed successfully!')
            )
        elif dry_run:
            self.stdout.write(
                self.style.WARNING('\nDry run completed. Use without --dry-run to apply changes.')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\nNo changes made.')
            )
