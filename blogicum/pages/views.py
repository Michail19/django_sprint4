from django.shortcuts import render


def about(request):
    """Страница 'О нас'"""
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    """Страница 'Правила'"""
    template = 'pages/rules.html'
    return render(request, template)
