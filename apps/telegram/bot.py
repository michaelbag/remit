import requests
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from .models import TelegramUser, TelegramMessage, TelegramSubscriptionCategory, TelegramUserRole, TelegramPermission
from .services import TelegramSubscriptionService, TelegramRBACService

logger = logging.getLogger(__name__)


class TelegramBot:
    """Main class for working with Telegram Bot API"""
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.webhook_url = settings.TELEGRAM_WEBHOOK_URL
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.rbac_service = TelegramRBACService()
    
    def send_message(self, chat_id, text, parse_mode='HTML', reply_markup=None):
        """Send message to user"""
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
        """Set webhook"""
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
        """Get webhook information"""
        url = f"{self.api_url}/getWebhookInfo"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting webhook info: {e}")
            return {'ok': False, 'error': str(e)}
    
    def remove_webhook(self):
        """Remove webhook"""
        url = f"{self.api_url}/deleteWebhook"
        
        try:
            response = requests.post(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error removing webhook: {e}")
            return {'ok': False, 'error': str(e)}
    
    def get_chat_member_info(self, chat_id):
        """Get user information by chat_id"""
        url = f"{self.api_url}/getChat"
        data = {'chat_id': chat_id}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                chat_info = result.get('result', {})
                # Return information in format compatible with get_or_create_telegram_user
                return {
                    'id': chat_info.get('id'),
                    'username': chat_info.get('username', ''),
                    'first_name': chat_info.get('first_name', ''),
                    'last_name': chat_info.get('last_name', ''),
                    'type': chat_info.get('type', 'private')
                }
            else:
                logger.error(f"Error getting chat info: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting chat member info: {e}")
            return None
    
    def get_or_create_telegram_user(self, telegram_data):
        """Get or create Telegram user"""
        if not telegram_data or not telegram_data.get('id'):
            logger.error(f"Invalid telegram data: {telegram_data}")
            return None
            
        telegram_id = telegram_data.get('id')
        username = telegram_data.get('username', '')
        first_name = telegram_data.get('first_name', '')
        last_name = telegram_data.get('last_name', '')
        
        # Look for existing user
        try:
            telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
            # Update data
            telegram_user.username = username
            telegram_user.first_name = first_name
            telegram_user.last_name = last_name
            telegram_user.save()
            return telegram_user
        except TelegramUser.DoesNotExist:
            # Create new user
            # First create Django user
            django_username = f"telegram_{telegram_id}"
            django_user, created = User.objects.get_or_create(
                username=django_username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            
            # Update user info if it already existed
            if not created:
                django_user.first_name = first_name
                django_user.last_name = last_name
                django_user.save()
            
            # Create Telegram user
            telegram_user, created = TelegramUser.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'user': django_user,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            
            # Update user info if it already existed
            if not created:
                telegram_user.user = django_user
                telegram_user.username = username
                telegram_user.first_name = first_name
                telegram_user.last_name = last_name
                telegram_user.save()
            
            return telegram_user
    
    def find_employee_by_phone(self, phone_number):
        """Find employee by phone number"""
        from apps.org.models import Employee
        
        # Normalize phone number (use method from Employee model)
        temp_employee = Employee()
        normalized_phone = temp_employee.normalize_phone(phone_number)
        
        logger.info(f"Searching for employee with phone: {phone_number} -> normalized: {normalized_phone}")
        
        # Search for employee by normalized number
        try:
            employee = Employee.objects.get(phone=normalized_phone, archive=False)
            logger.info(f"Found employee: {employee.name} (PK: {employee.pk})")
            return employee
        except Employee.DoesNotExist:
            logger.warning(f"Employee not found for normalized phone: {normalized_phone}")
            return None
    
    def link_telegram_user_to_employee(self, telegram_user, phone_number):
        """Link Telegram user to employee by phone number"""
        employee = self.find_employee_by_phone(phone_number)
        if employee:
            telegram_user.employee = employee
            telegram_user.phone_number = phone_number
            telegram_user.save()
            return True
        return False
    
    def handle_message(self, message_data):
        """Process text message"""
        chat_id = message_data.get('chat', {}).get('id')
        text = message_data.get('text', '')
        message_id = message_data.get('message_id')
        from_user = message_data.get('from', {})
        
        # Get or create user
        telegram_user = self.get_or_create_telegram_user(from_user)
        if not telegram_user:
            logger.error(f"Failed to create/get telegram user for: {from_user}")
            return "Error: Unable to process user data"
        
        # Save message
        telegram_message = TelegramMessage.objects.create(
            telegram_user=telegram_user,
            message_id=message_id,
            message_type='text',
            content=text
        )
        
        # Process commands
        if text.startswith('/'):
            return self.handle_command(telegram_user, text, telegram_message)
        else:
            # Check if user is linked to employee
            if not telegram_user.employee:
                # Request contact information
                return self.request_contact_info(telegram_user, telegram_message)
            else:
                # Regular message from linked user
                response_text = _("Hello, {name}! I am the equipment management system bot.").format(name=telegram_user.employee.name)
                self.send_message(chat_id, response_text)
                telegram_message.response = response_text
                telegram_message.is_processed = True
                telegram_message.save()
                return response_text
    
    def handle_command(self, telegram_user, command, telegram_message):
        """Process commands"""
        chat_id = telegram_user.telegram_id
        
        if command == '/start':
            response_text = (
                _("🤖 <b>Welcome to the equipment management system!</b>\n\n"
                "Available commands:\n"
                "/help - Help\n"
                "/status - System status\n"
                "/equipment - Equipment list\n"
                "/subscriptions - Subscription management\n"
                "/mysubscriptions - My subscriptions\n"
                "/roles - My roles\n"
                "/permissions - My permissions\n"
                "/language - Change language\n"
                "/forgetme - Unlink profile from employee")
            )
        elif command == '/help':
            response_text = (
                _("📋 <b>Command help:</b>\n\n"
                "/start - Start working\n"
                "/help - Show this help\n"
                "/status - System status\n"
                "/equipment - Equipment list\n"
                "/subscriptions - Available subscriptions\n"
                "/mysubscriptions - My subscriptions\n"
                "/subscribe <code>code</code> - Subscribe to category\n"
                "/unsubscribe <code>code</code> - Unsubscribe from category\n"
                "/roles - My roles and groups\n"
                "/permissions - My permissions\n"
                "/language - Change language\n"
                "/forgetme - Unlink profile from employee")
            )
        elif command == '/status':
            response_text = _("✅ System is working normally")
        elif command == '/equipment':
            if telegram_user.employee:
                # Get employee equipment
                from apps.equipment.models import Equipment
                equipment_list = Equipment.objects.filter(
                    employee=telegram_user.employee,
                    archive=False
                ).order_by('equip_code')
                
                if equipment_list:
                    response_text = _("🖥️ <b>Your equipment:</b>\n\n")
                    for equipment in equipment_list:
                        response_text += f"• {equipment.equip_code} - {equipment.type.name if equipment.type else _('Not specified')}\n"
                        if equipment.serial_number:
                            response_text += f"  {_('Serial number')}: {equipment.serial_number}\n"
                        response_text += "\n"
                else:
                    response_text = _("📱 You have no assigned equipment")
            else:
                response_text = _("❌ You need to link your profile to an employee first")
        elif command == '/subscriptions':
            response_text = self.handle_subscriptions_command(telegram_user)
        elif command == '/mysubscriptions':
            response_text = self.handle_my_subscriptions_command(telegram_user)
        elif command.startswith('/subscribe '):
            category_code = command.split(' ', 1)[1]
            response_text = self.handle_subscribe_command(telegram_user, category_code)
        elif command.startswith('/unsubscribe '):
            category_code = command.split(' ', 1)[1]
            response_text = self.handle_unsubscribe_command(telegram_user, category_code)
        elif command == '/roles':
            response_text = self.get_user_roles_info(telegram_user)
        elif command == '/permissions':
            response_text = self.get_user_permissions_info(telegram_user)
        elif command == '/language':
            response_text = self.handle_language_command(telegram_user)
        elif command == '/forgetme':
            response_text = self.handle_forgetme_command(telegram_user)
        else:
            response_text = _("❓ Unknown command. Use /help for help.")
        
        # Send message only if response_text is not None
        if response_text is not None:
            self.send_message(chat_id, response_text)
            telegram_message.response = response_text
        else:
            # If response_text is None, message was already sent in command
            telegram_message.response = "Message sent with inline keyboard"
        
        telegram_message.message_type = 'command'
        telegram_message.is_processed = True
        telegram_message.save()
        
        return response_text
    
    def handle_update(self, update_data):
        """Process update from Telegram"""
        if 'message' in update_data:
            message_data = update_data['message']
            
            # Check if contact information exists
            if 'contact' in message_data:
                from_user = message_data.get('from', {})
                telegram_user = self.get_or_create_telegram_user(from_user)
                if not telegram_user:
                    logger.error(f"Failed to create/get telegram user for contact: {from_user}")
                    return "Error: Unable to process user data"
                return self.handle_contact(message_data['contact'], telegram_user)
            else:
                return self.handle_message(message_data)
                
        elif 'callback_query' in update_data:
            # Process callback queries
            callback_query = update_data['callback_query']
            chat_id = callback_query['message']['chat']['id']
            data = callback_query['data']
            from_user = callback_query.get('from', {})
            
            # Get user
            telegram_user = self.get_or_create_telegram_user(from_user)
            if not telegram_user:
                logger.error(f"Failed to create/get telegram user for callback: {from_user}")
                return "Error: Unable to process user data"
            
            # Process callback data
            response_text = self.handle_callback_query(telegram_user, data, callback_query)
            
            # Answer callback query (remove "loading" indicator in Telegram)
            self.answer_callback_query(callback_query['id'], response_text)
            
            return response_text
        
        return "Unknown update type"
    
    def request_contact_info(self, telegram_user, telegram_message):
        """Request contact information from user"""
        chat_id = telegram_user.telegram_id
        
        response_text = (
            _("👋 Welcome to the equipment management system!\n\n"
            "To access system functions, you need to verify your identity.\n"
            "Please share your phone number by clicking the button below:")
        )
        
        # Create keyboard with button for sending contact
        keyboard = {
            "keyboard": [[{
                "text": _("📱 Share phone number"),
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
        """Process contact information"""
        chat_id = telegram_user.telegram_id
        phone_number = contact_data.get('phone_number', '')
        
        logger.info(f"Received contact from user {telegram_user.telegram_id}: {phone_number}")
        
        if phone_number:
            # Try to find employee by phone number
            if self.link_telegram_user_to_employee(telegram_user, phone_number):
                response_text = (
                    _("✅ Great! You have been successfully linked to employee profile: {name}\n\n"
                    "Now you can use all bot functions:\n"
                    "/help - Command help\n"
                    "/equipment - Your equipment").format(name=telegram_user.employee.name)
                )
                logger.info(f"Successfully linked user {telegram_user.telegram_id} to employee {telegram_user.employee.name}")
            else:
                response_text = (
                    _("❌ Employee with this phone number was not found in the system.\n\n"
                    "Contact the administrator to add your phone number to the employee profile.")
                )
                logger.warning(f"Employee not found for phone number: {phone_number}")
        else:
            response_text = _("❌ Failed to get phone number. Please try again.")
            logger.error("No phone number in contact data")
        
        self.send_message(chat_id, response_text)
        return response_text
    
    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        """Answer callback query"""
        url = f"{self.api_url}/answerCallbackQuery"
        data = {
            'callback_query_id': callback_query_id,
            'show_alert': show_alert
        }
        if text:
            data['text'] = text
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error answering callback query: {e}")
            return {'ok': False, 'error': str(e)}
    
    def handle_callback_query(self, telegram_user, data, callback_query):
        """Process callback queries from inline buttons"""
        chat_id = telegram_user.telegram_id
        
        if data.startswith('subscribe_'):
            # Subscribe to category
            category_code = data.replace('subscribe_', '')
            result = self.handle_subscribe_command(telegram_user, category_code)
            # Send notification to user
            self.send_message(chat_id, result)
            return result
            
        elif data.startswith('unsubscribe_'):
            # Unsubscribe from category
            category_code = data.replace('unsubscribe_', '')
            result = self.handle_unsubscribe_command(telegram_user, category_code)
            # Send notification to user
            self.send_message(chat_id, result)
            return result
            
        elif data.startswith('status_'):
            # Show subscription status
            category_code = data.replace('status_', '')
            try:
                from .models import TelegramSubscriptionCategory
                category = TelegramSubscriptionCategory.objects.get(code=category_code)
                subscription = TelegramSubscriptionService.get_user_subscription(telegram_user, category_code)
                
                if subscription:
                    status_emoji = {
                        'active': '✅',
                        'paused': '⏸️',
                        'pending': '⏳',
                        'unsubscribed': '❌'
                    }.get(subscription.status, '❓')
                    
                    result = _("{status_emoji} Subscription to '{category_name}' has status: {status}").format(
                        status_emoji=status_emoji, 
                        category_name=category.name, 
                        status=subscription.get_status_display()
                    )
                else:
                    result = _("❌ Subscription to '{category_name}' not found").format(category_name=category.name)
                
                # Send notification to user
                self.send_message(chat_id, result)
                return result
            except Exception as e:
                result = _("❌ Error getting subscription status: {error}").format(error=str(e))
                self.send_message(chat_id, result)
                return result
                
        elif data.startswith('lang_'):
            # Handle language change
            new_language = data.replace('lang_', '')
            return self.handle_language_change(telegram_user, new_language, callback_query)
        
        else:
            result = _("❓ Unknown command: {data}").format(data=data)
            self.send_message(chat_id, result)
            return result
    
    def handle_subscriptions_command(self, telegram_user):
        """Process /subscriptions command"""
        categories = TelegramSubscriptionService.get_available_categories()
        
        if not categories:
            return _("📢 No available subscription categories")
        
        # Get current user subscriptions
        user_subscriptions = TelegramSubscriptionService.get_user_subscriptions(telegram_user)
        user_subscription_codes = {sub.category.code: sub.status for sub in user_subscriptions}
        
        response_text = _("📢 <b>Available subscription categories:</b>\n\n")
        
        # Create inline keyboard
        keyboard = []
        
        for category in categories:
            response_text += f"{category.icon} <b>{category.name}</b>\n"
            if category.description:
                response_text += _("Description: {description}\n").format(description=category.description)
            
            # Determine subscription status and create button
            subscription_status = user_subscription_codes.get(category.code, 'not_subscribed')
            
            if subscription_status == 'active':
                response_text += _("Status: ✅ Subscribed\n")
                button_text = _("❌ Unsubscribe from {category_name}").format(category_name=category.name)
                callback_data = f"unsubscribe_{category.code}"
            elif subscription_status == 'paused':
                response_text += _("Status: ⏸️ Paused\n")
                button_text = _("▶️ Resume {category_name}").format(category_name=category.name)
                callback_data = f"subscribe_{category.code}"
            elif subscription_status == 'pending':
                response_text += _("Status: ⏳ Pending approval\n")
                button_text = _("⏳ {category_name} (pending)").format(category_name=category.name)
                callback_data = f"status_{category.code}"
            else:
                response_text += _("Status: ❌ Not subscribed\n")
                button_text = _("✅ Subscribe to {category_name}").format(category_name=category.name)
                callback_data = f"subscribe_{category.code}"
            
            # Add button to keyboard
            keyboard.append([{
                "text": button_text,
                "callback_data": callback_data
            }])
            
            response_text += "\n"
        
        response_text += _("💡 <i>Use the buttons below for quick subscription management</i>")
        
        # Create inline keyboard
        reply_markup = {
            "inline_keyboard": keyboard
        }
        
        # Send message with buttons
        chat_id = telegram_user.telegram_id
        self.send_message(chat_id, response_text, reply_markup=reply_markup)
        
        # Return None to avoid message duplication
        return None
    
    def handle_my_subscriptions_command(self, telegram_user):
        """Process /mysubscriptions command"""
        subscriptions = TelegramSubscriptionService.get_user_subscriptions(telegram_user)
        
        if not subscriptions:
            return "📭 У вас нет активных подписок. Используйте /subscriptions для просмотра доступных категорий."
        
        response_text = "📋 <b>Ваши подписки:</b>\n\n"
        
        # Create inline keyboard for subscription management
        keyboard = []
        
        for subscription in subscriptions:
            status_emoji = {
                'active': '✅',
                'paused': '⏸️',
                'pending': '⏳',
                'unsubscribed': '❌'
            }.get(subscription.status, '❓')
            
            response_text += f"{status_emoji} {subscription.category.icon} <b>{subscription.category.name}</b>\n"
            response_text += f"Статус: {subscription.get_status_display()}\n"
            response_text += f"Подписаны: {subscription.subscribed_at.strftime('%d.%m.%Y %H:%M')}\n"
            response_text += f"Уведомлений получено: {subscription.notification_count}\n"
            
            # Create buttons depending on status
            if subscription.status == 'active':
                button_text = f"❌ Отписаться от {subscription.category.name}"
                callback_data = f"unsubscribe_{subscription.category.code}"
            elif subscription.status == 'paused':
                button_text = f"▶️ Возобновить {subscription.category.name}"
                callback_data = f"subscribe_{subscription.category.code}"
            else:
                button_text = f"ℹ️ Статус {subscription.category.name}"
                callback_data = f"status_{subscription.category.code}"
            
            keyboard.append([{
                "text": button_text,
                "callback_data": callback_data
            }])
            
            response_text += "\n"
        
        response_text += "💡 <i>Используйте кнопки ниже для управления подписками</i>"
        
        # Create inline keyboard
        reply_markup = {
            "inline_keyboard": keyboard
        }
        
        # Send message with buttons
        chat_id = telegram_user.telegram_id
        self.send_message(chat_id, response_text, reply_markup=reply_markup)
        
        # Return None to avoid message duplication
        return None
    
    def handle_subscribe_command(self, telegram_user, category_code):
        """Process /subscribe command"""
        # Get current subscription before change
        current_subscription = TelegramSubscriptionService.get_user_subscription(telegram_user, category_code)
        
        subscription, created = TelegramSubscriptionService.subscribe_user(telegram_user, category_code)
        
        if subscription is None:
            return f"❌ <b>Ошибка подписки</b>\n\nКатегория с кодом '{category_code}' не найдена. Проверьте правильность кода."
        
        if created:
            # New subscription created
            if subscription.status == 'pending':
                return (
                    f"⏳ <b>Запрос на подписку отправлен</b>\n\n"
                    f"Вы подали заявку на подписку к категории:\n"
                    f"📢 <b>{subscription.category.name}</b>\n\n"
                    f"Ваш запрос будет рассмотрен администратором. "
                    f"Вы получите уведомление о результате."
                )
            else:
                return (
                    f"✅ <b>Подписка активирована</b>\n\n"
                    f"Вы успешно подписались на категорию:\n"
                    f"📢 <b>{subscription.category.name}</b>\n\n"
                    f"Теперь вы будете получать уведомления по этой категории."
                )
        else:
            # Subscription already exists, check what changed
            if current_subscription and current_subscription.status == 'unsubscribed':
                # User was unsubscribed, now subscribed
                if subscription.status == 'pending':
                    return (
                        f"⏳ <b>Запрос на подписку отправлен</b>\n\n"
                        f"Вы подали заявку на подписку к категории:\n"
                        f"📢 <b>{subscription.category.name}</b>\n\n"
                        f"Ваш запрос будет рассмотрен администратором. "
                        f"Вы получите уведомление о результате."
                    )
                else:
                    return (
                        f"✅ <b>Вы теперь подписаны</b>\n\n"
                        f"Вы подписались на категорию:\n"
                        f"📢 <b>{subscription.category.name}</b>\n\n"
                        f"Теперь вы будете получать уведомления по этой категории."
                    )
            elif current_subscription and current_subscription.status == 'paused':
                # User resumes paused subscription
                return (
                    f"▶️ <b>Подписка возобновлена</b>\n\n"
                    f"Подписка на категорию возобновлена:\n"
                    f"📢 <b>{subscription.category.name}</b>\n\n"
                    f"Уведомления снова активны."
                )
            else:
                # User already subscribed
                return (
                    f"ℹ️ <b>Подписка уже активна</b>\n\n"
                    f"Вы уже подписаны на категорию:\n"
                    f"📢 <b>{subscription.category.name}</b>\n\n"
                    f"Статус: {subscription.get_status_display()}"
                )
    
    def handle_unsubscribe_command(self, telegram_user, category_code):
        """Process /unsubscribe command"""
        success = TelegramSubscriptionService.unsubscribe_user(telegram_user, category_code)
        
        if success:
            try:
                category = TelegramSubscriptionCategory.objects.get(code=category_code)
                return (
                    f"❌ <b>Подписка отменена</b>\n\n"
                    f"Вы отписались от категории:\n"
                    f"📢 <b>{category.name}</b>\n\n"
                    f"Вы больше не будете получать уведомления по этой категории.\n"
                    f"Для повторной подписки используйте команду /subscriptions"
                )
            except TelegramSubscriptionCategory.DoesNotExist:
                return (
                    f"❌ <b>Подписка отменена</b>\n\n"
                    f"Вы отписались от категории с кодом '{category_code}'.\n\n"
                    f"Вы больше не будете получать уведомления по этой категории."
                )
        else:
            return (
                f"❌ <b>Ошибка отписки</b>\n\n"
                f"Подписка на категорию '{category_code}' не найдена.\n"
                f"Возможно, вы уже не подписаны на эту категорию."
            )
    
    def send_broadcast(self, broadcast):
        """Send broadcast"""
        from .services import TelegramBroadcastService
        broadcast_service = TelegramBroadcastService()
        return broadcast_service.send_broadcast(broadcast.id)
    
    def send_individual_message(self, telegram_user, message, parse_mode='HTML'):
        """Send individual message"""
        return self.send_message(telegram_user.telegram_id, message, parse_mode)
    
    def get_user_subscriptions(self, telegram_user):
        """Get user subscriptions"""
        return TelegramSubscriptionService.get_user_subscriptions(telegram_user)
    
    def subscribe_user(self, telegram_user, category_code):
        """Subscribe user to category"""
        return TelegramSubscriptionService.subscribe_user(telegram_user, category_code)
    
    def unsubscribe_user(self, telegram_user, category_code):
        """Unsubscribe user from category"""
        return TelegramSubscriptionService.unsubscribe_user(telegram_user, category_code)
    
    def check_permission(self, telegram_user, permission_code):
        """Check user permission"""
        return self.rbac_service.check_permission(telegram_user, permission_code)
    
    def log_command_execution(self, telegram_user, command, success=True, error_message=''):
        """Log command execution"""
        self.rbac_service.log_audit_action(
            telegram_user=telegram_user,
            action_type='command',
            action=f'Execute command: {command}',
            details={'command': command},
            success=success,
            error_message=error_message
        )
    
    def handle_command_with_permission(self, telegram_user, command, permission_code, command_handler):
        """Execute command with permission check"""
        # Check permission
        if not self.check_permission(telegram_user, permission_code):
            response_text = (
                _("❌ You don't have permission to execute command {command}.\n"
                "Contact the administrator to get the necessary permissions.").format(command=command)
            )
            self.send_message(telegram_user.telegram_id, response_text)
            self.log_command_execution(telegram_user, command, success=False, 
                                     error_message="Permission denied")
            return response_text
        
        # Execute command
        try:
            response_text = command_handler(telegram_user)
            self.log_command_execution(telegram_user, command, success=True)
            return response_text
        except Exception as e:
            error_msg = f"Error executing command {command}: {str(e)}"
            logger.error(error_msg)
            response_text = _("❌ An error occurred while executing the command: {error}").format(error=str(e))
            self.send_message(telegram_user.telegram_id, response_text)
            self.log_command_execution(telegram_user, command, success=False, 
                                     error_message=error_msg)
            return response_text
    
    def get_user_roles_info(self, telegram_user):
        """Get user roles information"""
        roles = telegram_user.get_all_roles()
        groups = telegram_user.get_active_groups()
        
        if not roles:
            return _("You have no assigned roles. Contact the administrator.")
        
        response_text = _("👤 <b>Your roles and groups:</b>\n\n")
        
        # Show roles
        response_text += _("🔑 <b>Roles:</b>\n")
        for role in roles:
            role_display = dict(TelegramUserRole.choices).get(role, role)
            response_text += f"• {role_display}\n"
        
        # Show groups
        if groups:
            response_text += _("\n👥 <b>Groups:</b>\n")
            for membership in groups:
                response_text += f"• {membership.group.name}\n"
        
        return response_text
    
    def get_user_permissions_info(self, telegram_user):
        """Get user permissions information"""
        permissions = self.rbac_service.get_user_effective_permissions(telegram_user)
        
        if not permissions:
            return _("You have no active permissions.")
        
        response_text = _("🔐 <b>Your permissions:</b>\n\n")
        
        # Group permissions by type
        permission_types = {}
        for perm in permissions:
            if perm.permission_type not in permission_types:
                permission_types[perm.permission_type] = []
            permission_types[perm.permission_type].append(perm)
        
        for perm_type, perms in permission_types.items():
            type_display = dict(TelegramPermission.PERMISSION_TYPES).get(perm_type, perm_type)
            response_text += f"📋 <b>{type_display}:</b>\n"
            for perm in perms:
                response_text += f"• {perm.name}\n"
            response_text += "\n"
        
        return response_text
    
    def handle_forgetme_command(self, telegram_user):
        """Process /forgetme command - unlink from employee"""
        try:
            # Check if user is linked to employee
            if not telegram_user.employee:
                return (
                    _("ℹ️ <b>Your profile is not linked to an employee</b>\n\n"
                    "No need to unlink, as the profile is already not connected to an employee.")
                )
            
            # Save employee information for message
            employee_name = telegram_user.employee.name if telegram_user.employee else _("Unknown")
            
            # Unlink from employee
            telegram_user.employee = None
            
            # Clear phone number
            telegram_user.phone_number = ""
            
            # Save changes
            telegram_user.save()
            
            # Log action
            logger.info(f"User {telegram_user.telegram_id} unlinked from employee {employee_name}")
            
            return (
                _("✅ <b>Profile successfully unlinked!</b>\n\n"
                f"You are no longer connected to employee: <b>{employee_name}</b>\n"
                "Phone number removed from profile.\n\n"
                "For re-linking, contact the administrator or use the /start command")
            )
            
        except Exception as e:
            logger.error(f"Error in handle_forgetme_command: {e}")
            return (
                _("❌ <b>An error occurred while unlinking the profile</b>\n\n"
                "Please try again later or contact the administrator.")
            )
    
    def handle_language_command(self, telegram_user):
        """Handle language change command"""
        try:
            chat_id = telegram_user.telegram_id
            
            # Create inline keyboard with language options
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "🇷🇺 Русский", "callback_data": "lang_ru"},
                        {"text": "🇺🇸 English", "callback_data": "lang_en"}
                    ]
                ]
            }
            
            # Send message with language selection
            current_lang = telegram_user.language
            current_lang_name = "Русский" if current_lang == 'ru' else "English"
            
            message_text = _("🌐 <b>Change Language / Изменить язык</b>\n\n"
                           "Current language: <b>{current}</b>\n"
                           "Select your preferred language:\n\n"
                           "Текущий язык: <b>{current}</b>\n"
                           "Выберите предпочитаемый язык:").format(current=current_lang_name)
            
            self.send_message(chat_id, message_text, reply_markup=keyboard)
            
            # Don't return response_text as we're sending a message with keyboard
            return None
            
        except Exception as e:
            logger.error(f"Error in handle_language_command: {e}")
            return _("❌ Error occurred while changing language. Please try again later.")
    
    def handle_language_change(self, telegram_user, new_language, callback_query):
        """Handle language change from callback"""
        try:
            chat_id = telegram_user.telegram_id
            
            # Validate language
            if new_language not in ['ru', 'en']:
                result = _("❌ Invalid language selection")
                self.send_message(chat_id, result)
                return result
            
            # Update user language
            telegram_user.language = new_language
            telegram_user.save()
            
            # Get language names
            lang_names = {
                'ru': 'Русский',
                'en': 'English'
            }
            
            # Send confirmation message
            if new_language == 'ru':
                result = (
                    "✅ <b>Язык успешно изменен!</b>\n\n"
                    f"Текущий язык: <b>{lang_names[new_language]}</b>\n"
                    "Все сообщения бота теперь будут на русском языке.\n\n"
                    "Language successfully changed!\n"
                    f"Current language: <b>{lang_names[new_language]}</b>"
                )
            else:  # English
                result = (
                    "✅ <b>Language successfully changed!</b>\n\n"
                    f"Current language: <b>{lang_names[new_language]}</b>\n"
                    "All bot messages will now be in English.\n\n"
                    "Язык успешно изменен!\n"
                    f"Текущий язык: <b>{lang_names[new_language]}</b>"
                )
            
            self.send_message(chat_id, result)
            
            # Log action
            logger.info(f"User {telegram_user.telegram_id} changed language to {new_language}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in handle_language_change: {e}")
            result = _("❌ Error occurred while changing language. Please try again later.")
            self.send_message(telegram_user.telegram_id, result)
            return result
