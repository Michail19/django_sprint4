from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from users import views as users_views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', users_views.RegistrationView.as_view(), name='registration'),
    path('profile/<str:username>/', users_views.profile, name='profile'),
    path('profile/<str:username>/edit/', users_views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/<str:username>/password/',
         auth_views.PasswordChangeView.as_view(
             template_name='users/password_change_form.html'
         ), name='password_change'),
]
