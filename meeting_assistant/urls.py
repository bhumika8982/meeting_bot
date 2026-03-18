from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/bot/', include('bot.urls')), # Sabhi APIs ab isi path par hain
    path('', TemplateView.as_view(template_name="bot/join_form.html"), name='home'),
]