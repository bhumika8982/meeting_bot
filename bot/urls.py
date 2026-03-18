from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_bot), 
    path('stop/<str:meeting_id>/', views.stop_bot_service),
    path('results/<str:meeting_id>/', views.get_meeting_results),
    path('delete/<str:meeting_id>/', views.delete_meeting_data),
]