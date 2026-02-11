from django.urls import path
from django.views.csrf import csrf_failure
from . import views

app_name = 'pages'

urlpatterns = [
    path('403csrf/', csrf_failure, name='csrf_failure'),
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
]
