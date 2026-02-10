from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/registration_form.html'

def profile(request, username):
    user = get_object_or_404(User, username=username)

    context = {
        'profile_user': user,
        'is_owner': request.user.is_authenticated and request.user == user,
        # 'posts': posts,
    }
    return render(request, 'users/profile.html', context)
