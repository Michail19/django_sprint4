from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.conf import settings

from .forms import RegistrationForm, ProfileUpdateForm
from blog.models import Post


class RegistrationView(CreateView):
    """Страница регистрации пользователя."""
    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляем уже аутентифицированных пользователей."""
        if request.user.is_authenticated:
            messages.info(request, 'Вы уже зарегистрированы.')
            return redirect('blog:index')  # Используем namespace
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Обработка успешной регистрации."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Регистрация прошла успешно! Теперь вы можете войти в систему.'
        )
        return response

    def get_success_url(self):
        return reverse('users:login')


@login_required
def profile(request, username):
    """Страница профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)

    # Получаем посты пользователя
    posts_query = Post.objects.all()

    # Если пользователь не владелец профиля, показываем только опубликованные посты
    if request.user == profile_user:
        posts_query = Post.objects.filter(author=profile_user)
    else:
        posts_query = Post.objects.filter(
            author=profile_user,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
            location__is_published=True
        )

    # Сортируем по дате публикации
    posts_query = posts_query.select_related('category', 'location').order_by('-pub_date')

    # Пагинация - 10 постов на страницу
    paginator = Paginator(posts_query, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
        'is_owner': request.user == profile_user,
    }
    return render(request, 'blog/profile.html', context)


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование профиля пользователя."""
    model = User
    form_class = ProfileUpdateForm
    template_name = 'blog/edit_profile.html'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def test_func(self):
        """Проверка, что пользователь редактирует свой профиль."""
        user = self.get_object()
        return self.request.user == user

    def handle_no_permission(self):
        """Обработка отсутствия прав доступа."""
        messages.error(self.request, 'Вы можете редактировать только свой профиль.')
        return redirect('users:profile', username=self.request.user.username)

    def form_valid(self, form):
        """Обработка успешного редактирования."""
        response = super().form_valid(form)
        messages.success(self.request, 'Профиль успешно обновлен!')
        return response

    def get_success_url(self):
        return reverse('users:profile', kwargs={'username': self.object.username})


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Кастомное представление для изменения пароля."""
    template_name = 'registration/password_change_form.html'

    def form_valid(self, form):
        """Обработка успешного изменения пароля."""
        response = super().form_valid(form)
        messages.success(self.request, 'Пароль успешно изменен!')
        return response

    def get_success_url(self):
        return reverse(
            'users:password_change_done',
            kwargs={'username': self.request.user.username}
        )


def password_change_done(request, username):
    """Страница успешного изменения пароля."""
    messages.success(request, 'Пароль успешно изменен!')
    return redirect('users:profile', username=request.user.username)
