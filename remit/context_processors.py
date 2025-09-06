from django.contrib import admin


def admin_app_list(request):
    if request.path.startswith("/admin/"):
        try:
            # Используем стандартный способ получения app_list
            template_response = admin.site.index(request)
            app_list = template_response.context_data.get("app_list", [])
            return {"app_list": app_list}
        except Exception as e:
            print(f"Error getting app list: {e}")
            return {"app_list": []}
    return {"app_list": []}
