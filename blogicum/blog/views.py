from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment


def index(request):
    """Главная страница блога - все посты"""
    post_list = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category', 'location', 'author') \
     .order_by('-pub_date')

    # Пагинация
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    """Детальная страница поста"""
    # Для автора показываем все посты, для остальных - только опубликованные
    if request.user.is_authenticated:
        # Автор видит все свои посты
        post = Post.objects.select_related('category', 'location', 'author').filter(
            pk=post_id
        ).first()
        if not post:
            # Если не найден пост с таким pk, пробуем среди опубликованных
            post = get_object_or_404(
                Post.objects.filter(
                    is_published=True,
                    category__is_published=True,
                    pub_date__lte=timezone.now()
                ).select_related('category', 'location', 'author'),
                pk=post_id
            )
    else:
        # Для неавторизованных — только опубликованные
        post = get_object_or_404(
            Post.objects.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ).select_related('category', 'location', 'author'),
            pk=post_id
        )

    comments = post.comments.all()

    comment_form = CommentForm() if request.user.is_authenticated else None

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': comment_form,
    })


def category_posts(request, category_slug):
    """Посты по категории"""
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )

    post_list = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category', 'location', 'author') \
        .order_by('-pub_date')

    # Пагинация
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'blog/category.html'
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# В PostCreateView исправляем get_success_url:
class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        if form.instance.pub_date > timezone.now():
            send_mail(
                'Пост запланирован',
                f'Ваш пост "{form.instance.title}" будет опубликован {form.instance.pub_date.strftime("%d.%m.%Y %H:%M")}',
                settings.DEFAULT_FROM_EMAIL,
                [self.request.user.email],
                fail_silently=True,
            )
        else:
            form.instance.is_published = True

        messages.success(self.request, 'Пост успешно создан!')
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('users:profile', kwargs={'username': self.request.user.username})  # Используем namespace


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование поста"""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Пост успешно отредактирован!')
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


@login_required
def delete_post(request, post_id):
    """Удаление поста"""
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален!')
        return redirect('users:profile', username=request.user.username)  # Используем namespace

    comment_form = None
    if request.user.is_authenticated:
        comment_form = CommentForm()

    # Отображаем страницу подтверждения удаления
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': comment_form,
        'confirm_delete': True
    })


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            # Отправляем уведомление автору поста
            if post.author.email and post.author != request.user:
                send_mail(
                    'Новый комментарий',
                    f'К вашему посту "{post.title}" добавили новый комментарий.',
                    settings.DEFAULT_FROM_EMAIL,
                    [post.author.email],
                    fail_silently=True,
                )

            messages.success(request, 'Комментарий успешно добавлен!')

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария"""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий успешно отредактирован!')
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    # Используем шаблон comment.html для редактирования
    return render(request, 'blog/comment.html', {
        'form': form,
        'post': post,
        'comment': comment,
        'editing': True,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий успешно удален!')
        return redirect('blog:post_detail', post_id=post_id)

    return redirect('blog:post_detail', post_id=post_id)


# Вспомогательные функции для работы с отложенными постами
def get_posts_for_user(user):
    """Возвращает посты для конкретного пользователя"""
    if user.is_authenticated:
        return Post.objects.filter(author=user).select_related('category', 'location', 'author')
    else:
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related('category', 'location', 'author')


def send_email_notification(subject, message, recipient):
    """Отправка email уведомления"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=True,
    )
