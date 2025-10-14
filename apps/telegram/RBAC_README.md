# Telegram RBAC (Role-Based Access Control) System

## Обзор

Система ролевого доступа (RBAC) для Telegram бота обеспечивает контроль доступа к различным функциям бота на основе ролей пользователей. Система позволяет гибко управлять правами доступа и обеспечивает аудит всех действий пользователей.

## Основные компоненты

### 1. Модели данных

#### TelegramUserRole (TextChoices)
Фиксированные роли для пользователей:
- `VIEWER` - Просмотрщик (базовые права просмотра)
- `USER` - Пользователь (стандартные права)
- `OPERATOR` - Оператор (управление оборудованием)
- `ADMIN` - Администратор (административные функции)
- `SUPER_ADMIN` - Супер-администратор (полные права)

#### TelegramUserGroup
Группы пользователей с назначенными ролями:
- `name` - название группы
- `description` - описание группы
- `roles` - список разрешенных ролей (JSON)
- `is_active` - активность группы

#### TelegramUserGroupMembership
Членство пользователей в группах:
- `telegram_user` - пользователь Telegram
- `group` - группа
- `assigned_roles` - назначенные роли (JSON)
- `assigned_by` - кто назначил
- `is_active` - активность членства

#### TelegramPermission
Разрешения для различных функций:
- `name` - название разрешения
- `code` - код разрешения
- `permission_type` - тип разрешения (command, feature, data_access, admin)
- `required_roles` - требуемые роли (JSON)
- `is_active` - активность разрешения

#### TelegramAuditLog
Логирование действий пользователей:
- `telegram_user` - пользователь
- `action_type` - тип действия
- `action` - описание действия
- `details` - детали действия (JSON)
- `success` - успешность выполнения
- `error_message` - сообщение об ошибке
- `ip_address` - IP адрес
- `user_agent` - User Agent

### 2. Сервисы

#### TelegramRBACService
Основной сервис для управления RBAC:

**Методы проверки разрешений:**
- `check_permission(telegram_user, permission_code)` - проверить разрешение
- `get_user_effective_permissions(telegram_user)` - получить все разрешения пользователя

**Методы управления группами:**
- `assign_user_to_group(telegram_user, group, roles, assigned_by)` - назначить в группу
- `remove_user_from_group(telegram_user, group, removed_by)` - удалить из группы

**Методы поиска пользователей:**
- `get_users_with_role(role)` - найти пользователей с ролью
- `get_users_with_permission(permission_code)` - найти пользователей с разрешением

**Методы инициализации:**
- `create_default_groups()` - создать группы по умолчанию
- `create_default_permissions()` - создать разрешения по умолчанию

**Методы аудита:**
- `log_audit_action()` - логировать действие
- `get_audit_logs()` - получить логи аудита

### 3. Интеграция с ботом

#### Новые методы TelegramBot:
- `check_permission(telegram_user, permission_code)` - проверка разрешений
- `handle_command_with_permission()` - выполнение команд с проверкой прав
- `get_user_roles_info()` - информация о ролях пользователя
- `get_user_permissions_info()` - информация о разрешениях пользователя
- `log_command_execution()` - логирование выполнения команд

#### Новые команды бота:
- `/roles` - показать роли и группы пользователя
- `/permissions` - показать разрешения пользователя

### 4. API Endpoints

#### Управление группами:
- `GET /api/rbac/groups/` - список групп
- `POST /api/rbac/assign-user/` - назначить пользователя в группу
- `POST /api/rbac/remove-user/` - удалить пользователя из группы

#### Управление разрешениями:
- `GET /api/rbac/user-permissions/<id>/` - разрешения пользователя
- `GET /api/rbac/permissions/` - список всех разрешений
- `GET /api/rbac/roles/` - доступные роли

#### Аудит:
- `GET /api/rbac/audit-logs/` - логи аудита

### 5. Административный интерфейс

#### TelegramUserGroupAdmin
- Управление группами пользователей
- Назначение ролей группам
- Просмотр количества участников

#### TelegramUserGroupMembershipAdmin
- Управление членством в группах
- Назначение ролей пользователям
- Отслеживание назначений

#### TelegramPermissionAdmin
- Управление разрешениями
- Настройка требуемых ролей
- Группировка по типам

#### TelegramAuditLogAdmin
- Просмотр логов аудита (только чтение)
- Фильтрация по пользователям и типам действий
- Детальная информация о действиях

## Установка и настройка

### 1. Применение миграций
```bash
python manage.py migrate telegram
```

### 2. Инициализация RBAC системы
```bash
python manage.py init_telegram_rbac
```

### 3. Назначение пользователей в группы
1. Перейдите в Django Admin
2. Откройте "Telegram User Group Memberships"
3. Добавьте пользователей в соответствующие группы
4. Назначьте роли для каждого пользователя

## Использование

### Проверка разрешений в коде
```python
from apps.telegram.services import TelegramRBACService

rbac_service = TelegramRBACService()

# Проверить разрешение
if rbac_service.check_permission(telegram_user, 'manage_equipment'):
    # Пользователь может управлять оборудованием
    pass
```

### Выполнение команд с проверкой прав
```python
# В обработчике команды бота
def handle_equipment_command(self, telegram_user):
    return self.handle_command_with_permission(
        telegram_user=telegram_user,
        command='/equipment',
        permission_code='view_equipment',
        command_handler=lambda user: self.get_equipment_list(user)
    )
```

### Назначение пользователя в группу
```python
from apps.telegram.models import TelegramUser, TelegramUserGroup
from apps.telegram.services import TelegramRBACService

rbac_service = TelegramRBACService()
telegram_user = TelegramUser.objects.get(id=1)
operators_group = TelegramUserGroup.objects.get(name='Operators')

membership, created = rbac_service.assign_user_to_group(
    telegram_user=telegram_user,
    group=operators_group,
    roles=['operator'],
    assigned_by=request.user
)
```

## Базовые группы и разрешения

### Группы по умолчанию:
1. **Viewers** - роли: `viewer`
2. **Users** - роли: `viewer`, `user`
3. **Operators** - роли: `viewer`, `user`, `operator`
4. **Admins** - роли: `viewer`, `user`, `operator`, `admin`
5. **Super Admins** - роли: `viewer`, `user`, `operator`, `admin`, `super_admin`

### Разрешения по умолчанию:
- `view_equipment` - просмотр оборудования (viewer+)
- `manage_equipment` - управление оборудованием (operator+)
- `view_subscriptions` - просмотр подписок (viewer+)
- `manage_subscriptions` - управление подписками (user+)
- `admin_panel` - доступ к админ-панели (admin+)
- `manage_users` - управление пользователями (admin+)
- `manage_broadcasts` - управление рассылками (admin+)
- `system_admin` - системное администрирование (super_admin)

## Безопасность

### Принципы безопасности:
- **Принцип минимальных привилегий** - пользователи получают только необходимые права
- **Разделение ролей** - четкое разделение между просмотром, управлением и администрированием
- **Аудит действий** - все действия логируются для отслеживания
- **Иерархия ролей** - роли имеют четкую иерархию с наследованием прав

### Рекомендации:
1. Регулярно проверяйте назначения ролей
2. Мониторьте логи аудита на предмет подозрительной активности
3. Используйте принцип минимальных привилегий
4. Регулярно обновляйте разрешения в соответствии с изменениями в системе

## Мониторинг и аудит

### Логирование действий:
- Выполнение команд бота
- Проверки разрешений
- Назначения ролей
- Изменения членства в группах
- Доступ к данным

### Фильтрация логов:
- По пользователю
- По типу действия
- По дате
- По успешности выполнения

### Аналитика:
- Статистика использования разрешений
- Анализ активности пользователей
- Выявление аномальной активности

## Расширение системы

### Добавление новых ролей:
1. Добавьте роль в `TelegramUserRole`
2. Создайте миграцию
3. Обновите группы и разрешения

### Добавление новых разрешений:
1. Создайте новое разрешение в админке
2. Настройте требуемые роли
3. Используйте в коде для проверки доступа

### Интеграция с внешними системами:
- API для управления ролями
- Webhook'и для уведомлений о изменениях
- Экспорт/импорт конфигурации ролей

## Troubleshooting

### Частые проблемы:

1. **Пользователь не может выполнить команду**
   - Проверьте назначенные роли
   - Убедитесь, что разрешение активно
   - Проверьте логи аудита

2. **Роли не применяются**
   - Убедитесь, что членство в группе активно
   - Проверьте, что группа активна
   - Перезапустите бота

3. **Ошибки в логах аудита**
   - Проверьте настройки логирования
   - Убедитесь в корректности данных пользователя

### Отладка:
```python
# Проверить роли пользователя
user_roles = telegram_user.get_all_roles()
print(f"User roles: {user_roles}")

# Проверить разрешения
rbac_service = TelegramRBACService()
permissions = rbac_service.get_user_effective_permissions(telegram_user)
print(f"User permissions: {[p.code for p in permissions]}")

# Проверить членство в группах
groups = telegram_user.get_active_groups()
print(f"User groups: {[g.group.name for g in groups]}")
```
