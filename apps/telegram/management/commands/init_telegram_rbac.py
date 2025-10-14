from django.core.management.base import BaseCommand
from apps.telegram.services import TelegramRBACService


class Command(BaseCommand):
    help = 'Initialize Telegram RBAC system with default groups and permissions'

    def handle(self, *args, **options):
        """Инициализировать систему RBAC"""
        
        self.stdout.write("Initializing Telegram RBAC system...")
        
        rbac_service = TelegramRBACService()
        
        # Создаем группы по умолчанию
        self.stdout.write("Creating default groups...")
        created_groups = rbac_service.create_default_groups()
        
        for group in created_groups:
            self.stdout.write(
                self.style.SUCCESS(f'Created group: {group.name} with roles: {", ".join(group.roles)}')
            )
        
        # Создаем разрешения по умолчанию
        self.stdout.write("Creating default permissions...")
        created_permissions = rbac_service.create_default_permissions()
        
        for permission in created_permissions:
            self.stdout.write(
                self.style.SUCCESS(f'Created permission: {permission.name} ({permission.code})')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nRBAC system initialized successfully!\n'
                f'Created {len(created_groups)} groups\n'
                f'Created {len(created_permissions)} permissions'
            )
        )
        
        # Показываем информацию о ролях
        self.stdout.write("\nAvailable roles:")
        from apps.telegram.models import TelegramUserRole
        for role_code, role_name in TelegramUserRole.choices:
            self.stdout.write(f"  - {role_code}: {role_name}")
        
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Assign users to appropriate groups in Django admin")
        self.stdout.write("2. Configure permissions for specific bot commands")
        self.stdout.write("3. Test role-based access control")
