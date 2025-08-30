from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('chatbot/', views.chatbot, name='chatbot'),
    path('tickets/', views.support_tickets, name='tickets'),
    path('faq/', views.faq, name='faq'),
]





