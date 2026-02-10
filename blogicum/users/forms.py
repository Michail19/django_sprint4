from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    """Форма регистрации нового пользователя."""
    email = forms.EmailField(
        required=True,
        label='Адрес электронной почты',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@domain.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Фамилия',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Придумайте имя пользователя'
            }),
        }
        help_texts = {
            'username': 'Только буквы, цифры и символы @/./+/-/_',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настраиваем виджеты для полей паролей
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Придумайте пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })

        # Убираем стандартные help_text для полей паролей
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        """Проверка уникальности email."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_username(self):
        """Проверка уникальности имени пользователя."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def save(self, commit=True):
        """Сохранение пользователя с дополнительными полями."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(UserChangeForm):
    """Форма редактирования профиля пользователя."""
    # Убираем поле пароля
    password = None

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваша фамилия'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@domain.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем help_text для всех полей
        for field in self.fields.values():
            field.help_text = ''

    def clean_email(self):
        """Проверка уникальности email с исключением текущего пользователя."""
        email = self.cleaned_data.get('email')
        user_id = self.instance.id

        # Проверяем, существует ли email у другого пользователя
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_username(self):
        """Проверка уникальности имени пользователя с исключением текущего."""
        username = self.cleaned_data.get('username')
        user_id = self.instance.id

        if User.objects.filter(username=username).exclude(id=user_id).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username
