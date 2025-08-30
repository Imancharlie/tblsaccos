from django.urls import path
from . import views

app_name = 'shares'

urlpatterns = [
    path('buy/', views.buy_shares, name='buy_shares'),
    path('my-shares/', views.my_shares, name='my_shares'),
    path('history/', views.shares_history, name='shares_history'),
]





