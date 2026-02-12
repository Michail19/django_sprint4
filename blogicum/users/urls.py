from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Регистрация
    path('registration/', views.RegistrationView.as_view(), name='registration'),

    # Профиль пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<str:username>/password/',
         views.CustomPasswordChangeView.as_view(),
         name='password_change'),
    path('profile/<str:username>/password/done/',
         views.password_change_done,
         name='password_change_done'),

    # Восстановление пароля (добавляем)
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/auth/password_reset/done/'
         ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/auth/reset/done/'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
