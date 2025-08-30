from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # HR Officer URLs
    path('hr/workspace/', views.hr_workspace, name='hr_workspace'),
    
    # Loan Officer URLs
    path('loans/workspace/', views.loan_workspace, name='loan_workspace'),
    
    # Committee Member URLs
    path('committee/workspace/', views.committee_workspace, name='committee_workspace'),
    
    # Accountant URLs
    path('accountant/workspace/', views.accountant_workspace, name='accountant_workspace'),
    path('accountant/payment-history/', views.payment_history, name='payment_history'),
    
    # Admin URLs
    path('admin/panel/', views.admin_panel, name='admin_panel'),
    path('admin/user-management/', views.admin_user_management, name='admin_user_management'),
]




