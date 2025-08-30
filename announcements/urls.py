from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='list'),
    path('create/', views.create_announcement, name='create'),
    path('detail/<int:pk>/', views.announcement_detail, name='detail'),
    path('edit/<int:pk>/', views.edit_announcement, name='edit'),
    path('delete/<int:pk>/', views.delete_announcement, name='delete'),
]





