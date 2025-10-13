from django.db import models
from django.contrib.auth.models import User


class TelegramUser(models.Model):
    """Модель для хранения связи пользователей с Telegram"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    username = models.CharField(max_length=255, blank=True, verbose_name='Telegram Username')
    first_name = models.CharField(max_length=255, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=255, blank=True, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    employee = models.ForeignKey('org.Employee', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='telegram_users', verbose_name='Сотрудник')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ({self.telegram_id})"


class TelegramMessage(models.Model):
    """Модель для хранения сообщений Telegram"""
    MESSAGE_TYPES = [
        ('text', 'Текстовое сообщение'),
        ('command', 'Команда'),
        ('callback', 'Callback запрос'),
        ('error', 'Ошибка'),
    ]

    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='messages')
    message_id = models.BigIntegerField(verbose_name='ID сообщения')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, verbose_name='Тип сообщения')
    content = models.TextField(verbose_name='Содержимое')
    response = models.TextField(blank=True, verbose_name='Ответ бота')
    is_processed = models.BooleanField(default=False, verbose_name='Обработано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Telegram сообщение'
        verbose_name_plural = 'Telegram сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return f"Message {self.message_id} from {self.telegram_user.user.username}"
