from django.urls import path
from django.views.csrf import csrf_failure
from . import views

app_name = 'pages'

urlpatterns = [
    # Страница ошибки CSRF
    path('403csrf/', views.CsrfFailureView.as_view(), name='csrf_failure'),

    # Статические страницы с использованием CBV
    path('about/', views.AboutView.as_view(), name='about'),
    path('rules/', views.RulesView.as_view(), name='rules'),
]
