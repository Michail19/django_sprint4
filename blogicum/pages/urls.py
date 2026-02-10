from django.contrib import admin
from django.urls import path, include
from django.views.csrf import csrf_failure

app_name = 'pages'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('403csrf/', csrf_failure, name='csrf_failure'),
]
