# Telegram Bot для системы управления оборудованием

## Описание

Telegram бот для интеграции с системой управления оборудованием. Позволяет пользователям взаимодействовать с системой через Telegram.

## Настройка

### 1. Создание бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 2. Настройка параметров

В файле `remit/local_settings.py` укажите:

```python
# Telegram Bot settings
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'
TELEGRAM_WEBHOOK_URL = 'https://your-domain.com/telegram/webhook/'
```

### 3. Установка webhook

```bash
python manage.py setup_telegram_bot
```

### 4. Проверка webhook

```bash
python manage.py setup_telegram_bot --remove  # Удалить webhook
```

## API Endpoints

- `POST /telegram/webhook/` - Webhook для получения обновлений от Telegram
- `GET /telegram/set-webhook/` - Установка webhook
- `GET /telegram/webhook-info/` - Информация о webhook

## Команды бота

- `/start` - Начать работу с ботом
- `/help` - Справка по командам
- `/status` - Статус системы
- `/equipment` - Список оборудования (в разработке)

## Модели

### TelegramUser
Связывает пользователей Django с Telegram аккаунтами.

### TelegramMessage
Хранит историю сообщений и ответов бота.

## Админка

В Django админке доступны:
- Управление пользователями Telegram
- Просмотр истории сообщений
- Статистика использования бота

## Разработка

### Добавление новых команд

1. Добавьте обработку команды в метод `handle_command` в `bot.py`
2. Обновите справку в команде `/help`

### Добавление новых функций

1. Создайте новые методы в классе `TelegramBot`
2. Добавьте соответствующие URL в `urls.py`
3. Обновите документацию

## Безопасность

- Webhook защищен CSRF исключением
- Все сообщения логируются
- Пользователи создаются автоматически при первом обращении
