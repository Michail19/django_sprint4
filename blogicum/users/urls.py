from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Регистрация
    path('', views.RegistrationView.as_view(), name='registration'),

    # Профиль пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/<str:username>/password/',
         views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('profile/<str:username>/password/done/',
         views.password_change_done, name='password_change_done'),
]
