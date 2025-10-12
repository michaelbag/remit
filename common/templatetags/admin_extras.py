from django import template
from django.contrib.admin import site

register = template.Library()


@register.simple_tag(takes_context=True)
def get_admin_app_list(context):
    """
    Кастомный тег для получения списка приложений админки
    """
    try:
        request = context['request']
        app_list = site.get_app_list(request)
        return app_list
    except Exception as e:
        print(f"Error in get_admin_app_list: {e}")
        return []


@register.simple_tag(takes_context=True)
def is_current_model(context, model_dict):
    """
    Возвращает True, если текущий URL относится к списку данной модели в админке.
    Основано на сравнении начала request.path с model.admin_url.
    """
    try:
        request = context['request']
        admin_url = model_dict.get('admin_url')
        return bool(admin_url and request.path.startswith(admin_url))
    except Exception:
        return False


@register.simple_tag(takes_context=True)
def app_has_current(context, app_dict):
    """
    Возвращает True, если внутри приложения есть текущая активная модель.
    """
    try:
        request = context['request']
        path = request.path
        for m in app_dict.get('models', []):
            admin_url = m.get('admin_url')
            if admin_url and path.startswith(admin_url):
                return True
        return False
    except Exception:
        return False
