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
