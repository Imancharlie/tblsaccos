from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum
from loans.models import LoanApplication
from accounts.models import User, UserProfile

def is_hr_officer(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.user_type == 'hr_officer'

def is_loan_officer(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.user_type == 'loan_officer'

def is_committee_member(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.user_type == 'committee_member'

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.user_type == 'admin'

# HR Officer Views
@login_required
@user_passes_test(is_hr_officer)
def hr_workspace(request):
    # Get applications waiting for HR review
    pending_applications = LoanApplication.objects.filter(status='guarantor_approved')
    total_amount = sum(app.amount for app in pending_applications)
    
    context = {
        'pending_applications': pending_applications,
        'total_amount': total_amount,
        'total_applications': pending_applications.count(),
    }
    return render(request, 'staff/hr_workspace.html', context)

# Loan Officer Views
@login_required
@user_passes_test(is_loan_officer)
def loan_workspace(request):
    # Get applications waiting for loan officer review
    pending_applications = LoanApplication.objects.filter(status='hr_reviewed')
    total_amount = sum(app.amount for app in pending_applications)
    
    context = {
        'pending_applications': pending_applications,
        'total_amount': total_amount,
        'total_applications': pending_applications.count(),
    }
    return render(request, 'staff/loan_workspace.html', context)

# Committee Member Views
@login_required
@user_passes_test(is_committee_member)
def committee_workspace(request):
    # Get applications waiting for committee review
    pending_applications = LoanApplication.objects.filter(status='loan_officer_approved')
    total_amount = sum(app.amount for app in pending_applications)
    
    context = {
        'pending_applications': pending_applications,
        'total_amount': total_amount,
        'pending_decisions': pending_applications.count(),
    }
    return render(request, 'staff/committee_workspace.html', context)

# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    # Admin dashboard
    total_users = User.objects.count()
    total_loans = LoanApplication.objects.count()
    
    context = {
        'total_users': total_users,
        'total_loans': total_loans,
    }
    return render(request, 'staff/admin_panel.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_management(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'staff/admin_user_management.html', context)

# Accountant Views
@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type in ['accountant', 'admin'])
def accountant_workspace(request):
    # Get applications waiting for payment processing
    pending_applications = LoanApplication.objects.filter(status='committee_approved')
    total_amount = sum(app.final_approved_amount for app in pending_applications)
    
    context = {
        'pending_applications': pending_applications,
        'total_amount': total_amount,
        'pending_payments': pending_applications.count(),
    }
    return render(request, 'staff/accountant_workspace.html', context)

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type in ['accountant', 'admin'])
def payment_history(request):
    # Get all processed payments
    processed_applications = LoanApplication.objects.filter(status__in=['payment_processing', 'disbursed'])
    total_disbursed = sum(app.final_approved_amount for app in processed_applications if app.status == 'disbursed')
    
    context = {
        'processed_applications': processed_applications,
        'total_disbursed': total_disbursed,
    }
    return render(request, 'staff/payment_history.html', context)
