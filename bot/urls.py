from django.urls import path
from . import views

urlpatterns = [
    path('api/join/', views.start_bot, name='start_bot'),
    path('api/summary/<str:meeting_id>/', views.get_meeting_data, name='get_summary'),
    path('api/delete/<str:meeting_id>/', views.delete_meeting_data, name='delete_data'),
]