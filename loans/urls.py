from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('apply/', views.apply_loan, name='apply_loan'),
    path('my-loans/', views.my_loans, name='my_loans'),
    path('detail/<int:pk>/', views.application_detail, name='application_detail'),
    path('tracker/', views.application_tracker, name='application_tracker'),
    path('guarantor-approval/<int:pk>/', views.guarantor_approval, name='guarantor_approval'),
    path('hr-review/<int:pk>/', views.hr_review, name='hr_review'),
    path('loan-officer-review/<int:pk>/', views.loan_officer_review, name='loan_officer_review'),
    path('committee-review/<int:pk>/', views.committee_review, name='committee_review'),
    path('accountant-review/<int:pk>/', views.accountant_review, name='accountant_review'),
    path('disburse-loan/<int:pk>/', views.disburse_loan, name='disburse_loan'),
    path('export-pdf/<int:pk>/', views.export_pdf, name='export_pdf'),
    path('make-payment/<int:pk>/', views.make_payment, name='make_payment'),
    path('payment-history/<int:pk>/', views.payment_history, name='payment_history'),
    path('guarantor-requests/', views.guarantor_requests, name='guarantor_requests'),
    path('guarantor-approve-reject/<int:application_id>/', views.guarantor_approve_reject, name='guarantor_approve_reject'),
    path('api/search-members/', views.search_members, name='search_members'),
]

