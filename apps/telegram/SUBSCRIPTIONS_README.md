# Telegram Subscriptions and Broadcasting System

## Обзор

Система подписок и рассылок для Telegram бота позволяет пользователям подписываться на различные категории уведомлений и получать персонализированные сообщения.

## Основные компоненты

### 1. Модели данных

#### TelegramSubscriptionCategory
Категории подписок с настройками:
- `code` - уникальный код категории
- `name` - название категории
- `description` - описание
- `icon` - иконка для отображения
- `is_public` - публичная ли категория
- `requires_approval` - требует ли одобрения

#### TelegramUserSubscription
Подписки пользователей:
- `telegram_user` - пользователь Telegram
- `category` - категория подписки
- `status` - статус (active, paused, unsubscribed, pending)
- `notification_count` - количество полученных уведомлений
- `preferences` - пользовательские настройки

#### TelegramBroadcast
Рассылки сообщений:
- `title` - заголовок рассылки
- `message` - содержимое сообщения
- `broadcast_type` - тип рассылки
- `status` - статус (draft, scheduled, sending, sent, failed)
- `target_categories` - целевые категории
- `target_users` - целевые пользователи

#### TelegramBroadcastDelivery
Отслеживание доставки:
- `broadcast` - рассылка
- `telegram_user` - получатель
- `status` - статус доставки
- `error_message` - сообщение об ошибке

#### TelegramMessageTemplate
Шаблоны сообщений:
- `name` - название шаблона
- `category` - категория
- `subject_template` - шаблон заголовка
- `message_template` - шаблон сообщения
- `variables` - доступные переменные

### 2. Сервисы

#### TelegramSubscriptionService
Управление подписками:
- `get_available_categories()` - получить доступные категории
- `get_user_subscriptions(user)` - получить подписки пользователя
- `subscribe_user(user, category_code)` - подписать пользователя
- `unsubscribe_user(user, category_code)` - отписать пользователя
- `get_subscribers_for_category(category_code)` - получить подписчиков

#### TelegramBroadcastService
Управление рассылками:
- `create_broadcast()` - создать рассылку
- `send_broadcast(broadcast_id)` - отправить рассылку
- `schedule_broadcast()` - запланировать рассылку
- `get_broadcast_stats()` - получить статистику
- `retry_failed_deliveries()` - повторить неудачные доставки

#### TelegramNotificationService
Отправка уведомлений:
- `send_notification_to_category()` - отправить уведомление по категории
- `send_emergency_alert()` - отправить экстренное оповещение

### 3. API Endpoints

#### Подписки
- `GET /api/subscription-categories/` - список категорий
- `POST /api/subscription-categories/create/` - создать категорию
- `GET /api/user-subscriptions/` - подписки пользователя
- `POST /api/subscribe/` - подписаться
- `POST /api/unsubscribe/` - отписаться

#### Рассылки
- `GET /api/broadcasts/` - список рассылок
- `POST /api/broadcasts/create/` - создать рассылку
- `POST /api/broadcasts/<id>/send/` - отправить рассылку
- `GET /api/broadcasts/<id>/stats/` - статистика рассылки
- `GET /api/broadcasts/<id>/deliveries/` - детали доставки

#### Уведомления
- `POST /api/notifications/send/` - отправить уведомление
- `POST /api/notifications/emergency/` - экстренное оповещение

#### Статистика
- `GET /api/stats/subscriptions/` - статистика подписок

### 4. Команды бота

#### Новые команды
- `/subscriptions` - показать доступные категории подписок
- `/mysubscriptions` - показать мои подписки
- `/subscribe <код>` - подписаться на категорию
- `/unsubscribe <код>` - отписаться от категории

#### Примеры использования
```
/subscriptions
/mysubscriptions
/subscribe EQUIPMENT_ALERTS
/unsubscribe SYSTEM_NOTIFICATIONS
```

### 5. Административный интерфейс

#### Управление категориями
- Создание и редактирование категорий
- Настройка публичности и требований одобрения
- Просмотр статистики подписчиков

#### Управление рассылками
- Создание рассылок
- Выбор целевой аудитории
- Планирование отправки
- Мониторинг доставки

#### Управление подписками
- Просмотр подписок пользователей
- Управление статусами подписок
- Массовые операции

### 6. Базовые категории

Система поставляется с предустановленными категориями:

1. **EQUIPMENT_ALERTS** 🖥️ - Уведомления об оборудовании
2. **SYSTEM_NOTIFICATIONS** ⚙️ - Системные уведомления
3. **SECURITY_ALERTS** 🔒 - Безопасность (требует одобрения)
4. **ORGANIZATIONAL_NEWS** 📢 - Корпоративные новости
5. **PERSONAL_UPDATES** 👤 - Личные обновления
6. **TECHNICAL_NOTIFICATIONS** 🔧 - Технические уведомления (приватные)
7. **EMERGENCY_ALERTS** 🚨 - Экстренные оповещения

## Установка и настройка

### 1. Применение миграций
```bash
python manage.py migrate telegram
```

### 2. Инициализация категорий
```bash
python manage.py init_telegram_categories
```

### 3. Настройка прав доступа
Убедитесь, что пользователи имеют соответствующие права для:
- Создания рассылок (только администраторы)
- Управления категориями (только администраторы)
- Просмотра статистики (только администраторы)

## Использование

### Отправка уведомления по категории
```python
from apps.telegram.services import TelegramNotificationService

service = TelegramNotificationService()
service.send_notification_to_category(
    category_code='EQUIPMENT_ALERTS',
    message='Обновление статуса оборудования',
    title='Уведомление об оборудовании'
)
```

### Создание рассылки
```python
from apps.telegram.services import TelegramBroadcastService

service = TelegramBroadcastService()
broadcast = service.create_broadcast(
    title='Важное объявление',
    message='Содержимое сообщения',
    target_categories=[category1, category2]
)
service.send_broadcast(broadcast.id)
```

### Экстренное оповещение
```python
from apps.telegram.services import TelegramNotificationService

service = TelegramNotificationService()
service.send_emergency_alert(
    message='Критическая ситуация!',
    target_categories=['EMERGENCY_ALERTS']
)
```

## Безопасность

- Все API endpoints требуют аутентификации
- Административные функции доступны только администраторам
- Экстренные оповещения обходят настройки подписок
- Все операции логируются

## Мониторинг

- Отслеживание статуса доставки сообщений
- Статистика подписок и рассылок
- Логирование ошибок и неудачных доставок
- Аналитика вовлеченности пользователей

## Расширение

Система легко расширяется:
- Добавление новых категорий подписок
- Создание пользовательских шаблонов сообщений
- Интеграция с внешними системами уведомлений
- Настройка пользовательских предпочтений
