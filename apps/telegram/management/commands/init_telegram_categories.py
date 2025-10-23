from django.core.management.base import BaseCommand
from apps.telegram.models import TelegramSubscriptionCategory


class Command(BaseCommand):
    help = 'Initialize default Telegram subscription categories'

    def handle(self, *args, **options):
        """Создать базовые категории подписок"""
        
        categories = [
            {
                'code': 'EQUIPMENT_ALERTS',
                'name': 'Уведомления об оборудовании',
                'description': 'Уведомления о статусе оборудования, техническом обслуживании, ремонте',
                'icon': '🖥️',
                'is_public': True,
                'requires_approval': False,
            },
            {
                'code': 'SYSTEM_NOTIFICATIONS',
                'name': 'Системные уведомления',
                'description': 'Уведомления об обновлениях системы, окнах обслуживания',
                'icon': '⚙️',
                'is_public': True,
                'requires_approval': False,
            },
            {
                'code': 'SECURITY_ALERTS',
                'name': 'Безопасность',
                'description': 'Уведомления о безопасности, доступе, нарушениях',
                'icon': '🔒',
                'is_public': True,
                'requires_approval': True,
            },
            {
                'code': 'ORGANIZATIONAL_NEWS',
                'name': 'Корпоративные новости',
                'description': 'Новости компании, объявления, изменения в организации',
                'icon': '📢',
                'is_public': True,
                'requires_approval': False,
            },
            {
                'code': 'PERSONAL_UPDATES',
                'name': 'Личные обновления',
                'description': 'Персональные уведомления о назначенном оборудовании, задачах',
                'icon': '👤',
                'is_public': True,
                'requires_approval': False,
            },
            {
                'code': 'TECHNICAL_NOTIFICATIONS',
                'name': 'Технические уведомления',
                'description': 'Технические обновления, изменения API, техническая документация',
                'icon': '🔧',
                'is_public': False,
                'requires_approval': True,
            },
            {
                'code': 'EMERGENCY_ALERTS',
                'name': 'Экстренные оповещения',
                'description': 'Критические системные оповещения, экстренные ситуации',
                'icon': '🚨',
                'is_public': True,
                'requires_approval': False,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for category_data in categories:
            category, created = TelegramSubscriptionCategory.objects.get_or_create(
                code=category_data['code'],
                defaults=category_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name} ({category.code})')
                )
            else:
                # Обновляем существующую категорию
                for key, value in category_data.items():
                    if key != 'code':
                        setattr(category, key, value)
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated category: {category.name} ({category.code})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'Created: {created_count} categories\n'
                f'Updated: {updated_count} categories\n'
                f'Total: {TelegramSubscriptionCategory.objects.count()} categories'
            )
        )
