"""
URL configuration for remit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.conf import settings
# from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
# from hello.views import index as hello_index
# from config.views import index as config_index
from django.urls import include
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from . import settings
# from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('hello/', hello_index),
    # path('config/', config_index),
    # path('e/', include('apps.equipment.urls')),
    path('api/', include('api.urls')),
    # path('static/', serve, {'document_root': settings.STATIC_ROOT}),
    path('chaining/', include('smart_selects.urls')),
]

#TODO: Добавить URL паттерн по инструкции из https://django-smart-selects.readthedocs.io/en/latest/installation.html
#urlpatterns += (url(r'^chaining/', include('smart_selects.urls')),)
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += patterns('', (
#     r'^static/(?P<path>.*)$',
#     'django.views.static.serve',
#     {'document_root': settings.STATIC_ROOT}
# ))
