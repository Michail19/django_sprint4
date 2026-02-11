from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Страница 'О нас' - CBV версия."""
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Страница 'Правила' - CBV версия."""
    template_name = 'pages/rules.html'


class CsrfFailureView(TemplateView):
    template_name = 'pages/403csrf.html'
    status_code = 403

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('status', self.status_code)
        return super().render_to_response(context, **response_kwargs)


def csrf_failure(request, reason=''):
    """Кастомная страница ошибки CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Кастомная страница 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Кастомная страница 500."""
    return render(request, 'pages/500.html', status=500)
