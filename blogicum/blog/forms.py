from django import forms
from django.utils import timezone
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования постов."""
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = self.fields['category'].queryset.filter(is_published=True)
        self.fields['location'].queryset = self.fields['location'].queryset.filter(is_published=True)

    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'pub_date', 'location', 'category')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок поста'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7,
                'placeholder': 'Введите текст поста'
            }),
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'pub_date': 'Для отложенной публикации установите будущую дату',
            'image': 'Можно загрузить изображение в форматах JPG, PNG, GIF',
        }

    def clean_pub_date(self):
        """Валидация даты публикации."""
        pub_date = self.cleaned_data['pub_date']

        # Если пользователь не аутентифицирован (маловероятно в этом контексте)
        if pub_date > timezone.now() and (not self.user or not self.user.is_authenticated):
            raise forms.ValidationError(
                'Отложенные публикации могут создавать только авторизованные пользователи'
            )

        return pub_date


class CommentForm(forms.ModelForm):
    """Форма для создания и редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Оставьте ваш комментарий...',
                'maxlength': '1000'
            }),
        }
        help_texts = {
            'text': 'Максимальная длина комментария - 1000 символов',
        }

    def clean_text(self):
        """Валидация текста комментария."""
        text = self.cleaned_data['text'].strip()
        if len(text) < 3:
            raise forms.ValidationError('Комментарий должен содержать хотя бы 3 символа')
        if len(text) > 1000:
            raise forms.ValidationError('Комментарий не должен превышать 1000 символов')
        return text
