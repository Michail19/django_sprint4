from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500, handler403
from . import views

app_name = 'pages'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', include('users.urls')),
]

# Назначаем кастомные обработчики
handler403 = 'pages.views.custom_403'
handler404 = 'pages.views.custom_404'
handler500 = 'pages.views.custom_500'
