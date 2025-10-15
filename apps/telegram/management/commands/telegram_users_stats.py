from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.telegram.models import TelegramUser, TelegramMessage, TelegramUserSubscription, TelegramSubscriptionCategory
from django.db.models import Count, Q


class Command(BaseCommand):
    help = 'Show Telegram users statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze (default: 30)'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information'
        )

    def handle(self, *args, **options):
        days = options['days']
        detailed = options['detailed']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write('='*60)
        self.stdout.write('TELEGRAM USERS STATISTICS')
        self.stdout.write('='*60)
        
        # Общая статистика пользователей
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        inactive_users = total_users - active_users
        
        self.stdout.write(f'\n📊 USER STATISTICS:')
        self.stdout.write(f'Total users: {total_users}')
        self.stdout.write(f'Active users: {active_users}')
        self.stdout.write(f'Inactive users: {inactive_users}')
        
        # Статистика по сообщениям
        total_messages = TelegramMessage.objects.count()
        recent_messages = TelegramMessage.objects.filter(created_at__gte=cutoff_date).count()
        processed_messages = TelegramMessage.objects.filter(is_processed=True).count()
        
        self.stdout.write(f'\n💬 MESSAGE STATISTICS:')
        self.stdout.write(f'Total messages: {total_messages}')
        self.stdout.write(f'Messages in last {days} days: {recent_messages}')
        self.stdout.write(f'Processed messages: {processed_messages}')
        
        # Статистика по подпискам
        total_subscriptions = TelegramUserSubscription.objects.count()
        active_subscriptions = TelegramUserSubscription.objects.filter(status='active').count()
        total_categories = TelegramSubscriptionCategory.objects.count()
        active_categories = TelegramSubscriptionCategory.objects.filter(is_active=True).count()
        
        self.stdout.write(f'\n📢 SUBSCRIPTION STATISTICS:')
        self.stdout.write(f'Total subscriptions: {total_subscriptions}')
        self.stdout.write(f'Active subscriptions: {active_subscriptions}')
        self.stdout.write(f'Total categories: {total_categories}')
        self.stdout.write(f'Active categories: {active_categories}')
        
        # Статистика активности пользователей
        active_users_recent = TelegramUser.objects.filter(
            messages__created_at__gte=cutoff_date
        ).distinct().count()
        
        self.stdout.write(f'\n📈 ACTIVITY STATISTICS (last {days} days):')
        self.stdout.write(f'Users with messages: {active_users_recent}')
        
        if detailed:
            self.stdout.write(f'\n📋 DETAILED INFORMATION:')
            
            # Топ пользователей по количеству сообщений
            top_users = TelegramUser.objects.annotate(
                message_count=Count('messages')
            ).order_by('-message_count')[:10]
            
            self.stdout.write(f'\nTop 10 users by message count:')
            for i, user in enumerate(top_users, 1):
                self.stdout.write(f'{i:2d}. {user.get_full_display()} - {user.message_count} messages')
            
            # Статистика по категориям подписок
            category_stats = TelegramSubscriptionCategory.objects.annotate(
                subscriber_count=Count('subscribers', filter=Q(subscribers__status='active'))
            ).order_by('-subscriber_count')
            
            self.stdout.write(f'\nSubscription categories:')
            for category in category_stats:
                self.stdout.write(f'{category.icon} {category.name}: {category.subscriber_count} subscribers')
            
            # Пользователи с подписками
            users_with_subscriptions = TelegramUser.objects.annotate(
                subscription_count=Count('subscriptions', filter=Q(subscriptions__status='active'))
            ).filter(subscription_count__gt=0).order_by('-subscription_count')
            
            self.stdout.write(f'\nUsers with subscriptions:')
            for user in users_with_subscriptions:
                self.stdout.write(f'{user.get_full_display()}: {user.subscription_count} subscriptions')
            
            # Статистика по типам сообщений
            message_types = TelegramMessage.objects.values('message_type').annotate(
                count=Count('message_id')
            ).order_by('-count')
            
            self.stdout.write(f'\nMessage types:')
            for msg_type in message_types:
                self.stdout.write(f'{msg_type["message_type"]}: {msg_type["count"]} messages')
        
        # Рекомендации
        self.stdout.write(f'\n💡 RECOMMENDATIONS:')
        
        if inactive_users > 0:
            self.stdout.write(f'- Consider reviewing {inactive_users} inactive users')
        
        if recent_messages == 0:
            self.stdout.write(f'- No messages in the last {days} days - check bot activity')
        
        if active_subscriptions == 0:
            self.stdout.write(f'- No active subscriptions - consider promoting categories')
        
        if total_categories > active_categories:
            inactive_categories = total_categories - active_categories
            self.stdout.write(f'- {inactive_categories} categories are inactive')
        
        self.stdout.write('\n' + '='*60)
