from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError


def about(request):
    """Страница 'О нас'"""
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    """Страница 'Правила'"""
    template = 'pages/rules.html'
    return render(request, template)

def custom_403(request, exception=None):
    """Обработка ошибки 403 Forbidden (включая CSRF)"""
    return render(request, 'pages/403.html', status=403)


def custom_404(request, exception=None):
    """Обработка ошибки 404 Not Found"""
    return render(request, 'pages/404.html', status=404)


def custom_500(request):
    """Обработка ошибки 500 Internal Server Error"""
    return render(request, 'pages/500.html', status=500)
