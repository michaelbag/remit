import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth.models import User
from .models import TelegramUser, TelegramMessage
from .bot import TelegramBot

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    """Webhook для получения обновлений от Telegram"""
    try:
        # Получаем данные от Telegram
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Received webhook data: {data}")
        
        # Инициализируем бота
        bot = TelegramBot()
        
        # Обрабатываем обновление
        response = bot.handle_update(data)
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def set_webhook(request):
    """Установка webhook для Telegram бота"""
    try:
        bot = TelegramBot()
        result = bot.set_webhook()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Set webhook error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def get_webhook_info(request):
    """Получение информации о webhook"""
    try:
        bot = TelegramBot()
        result = bot.get_webhook_info()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Get webhook info error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
