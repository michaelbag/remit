import requests
import logging
from django.conf import settings
from django.contrib.auth.models import User
from .models import TelegramUser, TelegramMessage

logger = logging.getLogger(__name__)


class TelegramBot:
    """Основной класс для работы с Telegram Bot API"""
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.webhook_url = settings.TELEGRAM_WEBHOOK_URL
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, chat_id, text, parse_mode='HTML', reply_markup=None):
        """Отправка сообщения пользователю"""
        url = f"{self.api_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def set_webhook(self):
        """Установка webhook"""
        url = f"{self.api_url}/setWebhook"
        data = {
            'url': self.webhook_url
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error setting webhook: {e}")
            return {'ok': False, 'error': str(e)}
    
    def get_webhook_info(self):
        """Получение информации о webhook"""
        url = f"{self.api_url}/getWebhookInfo"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting webhook info: {e}")
            return {'ok': False, 'error': str(e)}
    
    def remove_webhook(self):
        """Удаление webhook"""
        url = f"{self.api_url}/deleteWebhook"
        
        try:
            response = requests.post(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error removing webhook: {e}")
            return {'ok': False, 'error': str(e)}
    
    def get_or_create_telegram_user(self, telegram_data):
        """Получение или создание пользователя Telegram"""
        telegram_id = telegram_data.get('id')
        username = telegram_data.get('username', '')
        first_name = telegram_data.get('first_name', '')
        last_name = telegram_data.get('last_name', '')
        
        # Ищем существующего пользователя
        try:
            telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
            # Обновляем данные
            telegram_user.username = username
            telegram_user.first_name = first_name
            telegram_user.last_name = last_name
            telegram_user.save()
            return telegram_user
        except TelegramUser.DoesNotExist:
            # Создаем нового пользователя
            # Сначала создаем Django пользователя
            django_user = User.objects.create_user(
                username=f"telegram_{telegram_id}",
                first_name=first_name,
                last_name=last_name
            )
            
            # Создаем Telegram пользователя
            telegram_user = TelegramUser.objects.create(
                user=django_user,
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            return telegram_user
    
    def find_employee_by_phone(self, phone_number):
        """Поиск сотрудника по номеру телефона"""
        from apps.org.models import Employee
        
        # Нормализуем номер телефона (используем метод из модели Employee)
        temp_employee = Employee()
        normalized_phone = temp_employee.normalize_phone(phone_number)
        
        logger.info(f"Searching for employee with phone: {phone_number} -> normalized: {normalized_phone}")
        
        # Ищем сотрудника по нормализованному номеру
        try:
            employee = Employee.objects.get(phone=normalized_phone, archive=False)
            logger.info(f"Found employee: {employee.name} (PK: {employee.pk})")
            return employee
        except Employee.DoesNotExist:
            logger.warning(f"Employee not found for normalized phone: {normalized_phone}")
            return None
    
    def link_telegram_user_to_employee(self, telegram_user, phone_number):
        """Привязка Telegram пользователя к сотруднику по номеру телефона"""
        employee = self.find_employee_by_phone(phone_number)
        if employee:
            telegram_user.employee = employee
            telegram_user.phone_number = phone_number
            telegram_user.save()
            return True
        return False
    
    def handle_message(self, message_data):
        """Обработка текстового сообщения"""
        chat_id = message_data.get('chat', {}).get('id')
        text = message_data.get('text', '')
        message_id = message_data.get('message_id')
        from_user = message_data.get('from', {})
        
        # Получаем или создаем пользователя
        telegram_user = self.get_or_create_telegram_user(from_user)
        
        # Сохраняем сообщение
        telegram_message = TelegramMessage.objects.create(
            telegram_user=telegram_user,
            message_id=message_id,
            message_type='text',
            content=text
        )
        
        # Обрабатываем команды
        if text.startswith('/'):
            return self.handle_command(telegram_user, text, telegram_message)
        else:
            # Проверяем, привязан ли пользователь к сотруднику
            if not telegram_user.employee:
                # Запрашиваем контактные данные
                return self.request_contact_info(telegram_user, telegram_message)
            else:
                # Обычное сообщение от привязанного пользователя
                response_text = f"Привет, {telegram_user.employee.name}! Я бот системы управления оборудованием."
                self.send_message(chat_id, response_text)
                telegram_message.response = response_text
                telegram_message.is_processed = True
                telegram_message.save()
                return response_text
    
    def handle_command(self, telegram_user, command, telegram_message):
        """Обработка команд"""
        chat_id = telegram_user.telegram_id
        
        if command == '/start':
            response_text = (
                "🤖 <b>Добро пожаловать в систему управления оборудованием!</b>\n\n"
                "Доступные команды:\n"
                "/help - Справка\n"
                "/status - Статус системы\n"
                "/equipment - Список оборудования"
            )
        elif command == '/help':
            response_text = (
                "📋 <b>Справка по командам:</b>\n\n"
                "/start - Начать работу\n"
                "/help - Показать эту справку\n"
                "/status - Статус системы\n"
                "/equipment - Список оборудования"
            )
        elif command == '/status':
            response_text = "✅ Система работает нормально"
        elif command == '/equipment':
            if telegram_user.employee:
                # Получаем оборудование сотрудника
                from apps.equipment.models import Equipment
                equipment_list = Equipment.objects.filter(
                    employee=telegram_user.employee,
                    archive=False
                ).order_by('equip_code')
                
                if equipment_list:
                    response_text = f"🖥️ <b>Ваше оборудование:</b>\n\n"
                    for equipment in equipment_list:
                        response_text += f"• {equipment.equip_code} - {equipment.type.name if equipment.type else 'Не указан'}\n"
                        if equipment.serial_number:
                            response_text += f"  Серийный номер: {equipment.serial_number}\n"
                        response_text += "\n"
                else:
                    response_text = "📱 У вас нет закрепленного оборудования"
            else:
                response_text = "❌ Сначала необходимо привязать ваш профиль к сотруднику"
        else:
            response_text = "❓ Неизвестная команда. Используйте /help для справки."
        
        self.send_message(chat_id, response_text)
        telegram_message.response = response_text
        telegram_message.message_type = 'command'
        telegram_message.is_processed = True
        telegram_message.save()
        
        return response_text
    
    def handle_update(self, update_data):
        """Обработка обновления от Telegram"""
        if 'message' in update_data:
            message_data = update_data['message']
            
            # Проверяем, есть ли контактные данные
            if 'contact' in message_data:
                from_user = message_data.get('from', {})
                telegram_user = self.get_or_create_telegram_user(from_user)
                return self.handle_contact(message_data['contact'], telegram_user)
            else:
                return self.handle_message(message_data)
                
        elif 'callback_query' in update_data:
            # Обработка callback запросов
            callback_query = update_data['callback_query']
            chat_id = callback_query['message']['chat']['id']
            data = callback_query['data']
            
            response_text = f"Callback: {data}"
            self.send_message(chat_id, response_text)
            return response_text
        
        return "Unknown update type"
    
    def request_contact_info(self, telegram_user, telegram_message):
        """Запрос контактных данных у пользователя"""
        chat_id = telegram_user.telegram_id
        
        response_text = (
            "👋 Добро пожаловать в систему управления оборудованием!\n\n"
            "Для доступа к функциям системы необходимо подтвердить вашу личность.\n"
            "Пожалуйста, поделитесь своим номером телефона, нажав кнопку ниже:"
        )
        
        # Создаем клавиатуру с кнопкой для отправки контакта
        keyboard = {
            "keyboard": [[{
                "text": "📱 Поделиться номером телефона",
                "request_contact": True
            }]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        
        self.send_message(chat_id, response_text, reply_markup=keyboard)
        telegram_message.response = response_text
        telegram_message.is_processed = True
        telegram_message.save()
        
        return response_text
    
    def handle_contact(self, contact_data, telegram_user):
        """Обработка контактных данных"""
        chat_id = telegram_user.telegram_id
        phone_number = contact_data.get('phone_number', '')
        
        logger.info(f"Received contact from user {telegram_user.telegram_id}: {phone_number}")
        
        if phone_number:
            # Пытаемся найти сотрудника по номеру телефона
            if self.link_telegram_user_to_employee(telegram_user, phone_number):
                response_text = (
                    f"✅ Отлично! Вы успешно привязаны к профилю сотрудника: {telegram_user.employee.name}\n\n"
                    "Теперь вы можете использовать все функции бота:\n"
                    "/help - Справка по командам\n"
                    "/equipment - Ваше оборудование"
                )
                logger.info(f"Successfully linked user {telegram_user.telegram_id} to employee {telegram_user.employee.name}")
            else:
                response_text = (
                    "❌ Сотрудник с таким номером телефона не найден в системе.\n\n"
                    "Обратитесь к администратору для добавления вашего номера телефона в профиль сотрудника."
                )
                logger.warning(f"Employee not found for phone number: {phone_number}")
        else:
            response_text = "❌ Не удалось получить номер телефона. Попробуйте еще раз."
            logger.error("No phone number in contact data")
        
        self.send_message(chat_id, response_text)
        return response_text
