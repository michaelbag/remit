import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.contrib import messages
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
        import traceback
        logger.error(f"Webhook error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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


@staff_member_required
@require_http_methods(["GET", "POST"])
def admin_send_broadcast(request, broadcast_id):
    """Отправка рассылки из админки"""
    from .models import TelegramBroadcast
    from .services import TelegramBroadcastService
    
    try:
        # Получаем рассылку
        try:
            broadcast = TelegramBroadcast.objects.get(guid=broadcast_id)
        except TelegramBroadcast.DoesNotExist:
            messages.error(request, 'Рассылка не найдена')
            return redirect('admin:telegram_telegrambroadcast_changelist')
        
        # Проверяем статус рассылки
        if broadcast.status not in ['draft', 'scheduled']:
            messages.error(request, f'Рассылка не может быть отправлена. Текущий статус: {broadcast.get_status_display()}')
            return redirect('admin:telegram_telegrambroadcast_changelist')
        
        # Отправляем рассылку
        broadcast_service = TelegramBroadcastService()
        result = broadcast_service.send_broadcast(broadcast_id)
        
        if result:
            messages.success(request, f'Рассылка "{broadcast.title}" успешно отправлена!')
        else:
            messages.error(request, f'Ошибка при отправке рассылки "{broadcast.title}"')
        
        # Перенаправляем обратно в админку
        return redirect('admin:telegram_telegrambroadcast_changelist')
        
    except Exception as e:
        logger.error(f"Admin send broadcast error: {str(e)}")
        messages.error(request, f'Ошибка при отправке рассылки: {str(e)}')
        return redirect('admin:telegram_telegrambroadcast_changelist')
