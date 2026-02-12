from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class PublishedModel(models.Model):
    """Абстрактная модель для полей is_published и created_at."""

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    """Модель тематической категории."""

    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    """Модель географической метки."""

    name = models.CharField(
        'Название места',
        max_length=256
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    """Модель публикации."""

    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'  # Добавляем related_name для удобства
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    # Добавляем поле для изображений
    image = models.ImageField(
        'Изображение',
        upload_to='posts_images/',
        blank=True,
        null=True,
        help_text='Загрузите изображение для публикации'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']
        # Для обеспечения уникальности slug (если будете использовать)
        # unique_together = ['author', 'title']

    def __str__(self):
        return self.title

    @property
    def comment_count(self):
        """Количество комментариев к посту."""
        return self.comments.count()

    def is_published_now(self):
        """Проверка, опубликован ли пост в данный момент."""
        return self.is_published and self.pub_date <= timezone.now()

    def can_be_viewed_by(self, user):
        """
        Проверка, может ли пользователь просматривать пост.
        Автор видит все свои посты, остальные - только опубликованные.
        """
        if user == self.author:
            return True
        return self.is_published_now() and self.category.is_published


class Comment(models.Model):
    """Модель комментария к публикации."""

    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)


    def __str__(self):
        return f'Комментарий {self.author} к посту "{self.post.title}"'

    def can_be_edited_by(self, user):
        """Проверка, может ли пользователь редактировать комментарий."""
        return user == self.author

    def can_be_deleted_by(self, user):
        """Проверка, может ли пользователь удалить комментарий."""
        return user == self.author
