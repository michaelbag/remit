from django.contrib import admin
from django.contrib.admin.sites import AdminSite


def admin_app_list(request):
    """
    Контекстный процессор для кастомного шаблона админки
    с сворачиваемыми приложениями
    """
    if request.path.startswith("/admin/"):
        try:
            # Получаем список приложений из админки
            admin_site = AdminSite()
            app_list = admin_site.get_app_list(request)
            
            # Добавляем дополнительную информацию для каждого приложения
            for app in app_list:
                for model in app['models']:
                    # Определяем, является ли модель активной
                    model['is_active'] = (
                        model.get('admin_url') in request.path or
                        model.get('name').lower() in request.path.lower()
                    )
                    
                    # Добавляем информацию о текущем пути
                    model['current_path'] = request.path
                    
                # Определяем, содержит ли приложение активную модель
                app['has_active_model'] = any(
                    model.get('is_active', False) for model in app['models']
                )
            
            return {
                "app_list": app_list,
                "current_path": request.path,
                "user": request.user,
            }
        except Exception as e:
            print(f"Error getting app list: {e}")
            return {"app_list": []}
    return {"app_list": []}
