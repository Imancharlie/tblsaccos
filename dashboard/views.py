from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from loans.models import LoanApplication, GuarantorApproval, HRReview, LoanOfficerReview, CommitteeReview, RepaymentSchedule, LoanPayment, AccountantReview
from accounts.models import UserProfile, MemberProfile
from django.db.models import Q, Sum

@login_required
def index(request):
    try:
        user_profile = request.user.profile
        user_type = user_profile.user_type
    except:
        user_type = 'member'
    
    # Get member information for all users (including staff)
    member_context = get_member_dashboard_data(request.user)
    
    # Get role-specific dashboard data
    if user_type == 'member':
        context = member_context
    elif user_type == 'hr_officer':
        context = get_hr_dashboard_data()
        # Merge member context with HR context
        context.update(member_context)
    elif user_type == 'loan_officer':
        context = get_loan_officer_dashboard_data()
        # Merge member context with loan officer context
        context.update(member_context)
    elif user_type == 'committee_member':
        context = get_committee_dashboard_data()
        # Merge member context with committee context
        context.update(member_context)
    elif user_type == 'admin':
        context = get_admin_dashboard_data()
        # Merge member context with admin context
        context.update(member_context)
    else:
        context = member_context
    
    context['user_type'] = user_type
    return render(request, 'dashboard/index.html', context)

def get_member_dashboard_data(user):
    try:
        member_profile = user.memberprofile
        total_savings = member_profile.total_savings
        total_shares = member_profile.total_shares
        total_loans = member_profile.total_loans
        available_balance = member_profile.available_balance
    except:
        total_savings = total_shares = total_loans = available_balance = 0
    
    # Get user's loan applications
    loan_applications = LoanApplication.objects.filter(applicant=user).order_by('-created_at')[:5]
    pending_applications = LoanApplication.objects.filter(applicant=user, status='pending').count()
    approved_applications = LoanApplication.objects.filter(applicant=user, status='committee_approved').count()
    
    # Get guarantor requests for this user
    guarantor_requests = LoanApplication.objects.filter(
        Q(guarantor_approvals__guarantor=user) & 
        Q(guarantor_approvals__approved_at__isnull=True)
    ).distinct().count()
    
    # Calculate total borrowed and total paid
    from django.db.models import Sum
    from loans.models import LoanPayment
    
    # Total borrowed: sum of all approved loan amounts
    total_borrowed = LoanApplication.objects.filter(
        applicant=user, 
        status__in=['committee_approved', 'payment_processing', 'disbursed', 'completed']
    ).aggregate(total=Sum('final_approved_amount'))['total'] or 0
    
    # Total paid: sum of all loan payments
    total_paid = LoanPayment.objects.filter(
        loan_application__applicant=user
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate loan progress percentage
    loan_progress_percentage = 0
    if total_borrowed > 0:
        loan_progress_percentage = (total_paid / total_borrowed) * 100
    
    # Get actual pending guarantor requests for display
    pending_guarantor_applications = LoanApplication.objects.filter(
        Q(guarantor_approvals__guarantor=user) & 
        Q(guarantor_approvals__approved_at__isnull=True)
    ).distinct()[:3]  # Show only 3 most recent
    
    # Calculate monthly deduction (total monthly repayment for active loans)
    monthly_deduction = LoanApplication.objects.filter(
        applicant=user, 
        status__in=['committee_approved', 'payment_processing', 'disbursed', 'completed']
    ).aggregate(total=Sum('monthly_repayment'))['total'] or 0
    
    return {
        'total_savings': total_savings,
        'total_shares': total_shares,
        'total_loans': total_loans,
        'available_balance': available_balance,
        'loan_applications': loan_applications,
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'total_borrowed': total_borrowed,
        'total_paid': total_paid,
        'loan_progress_percentage': loan_progress_percentage,
        'guarantor_requests': guarantor_requests,
        'pending_guarantor_applications': pending_guarantor_applications,
        'monthly_deduction': monthly_deduction,
        'outstanding_amount': total_borrowed - total_paid,
    }

def get_hr_dashboard_data():
    pending_applications = LoanApplication.objects.filter(status='guarantor_approved').count()
    hr_reviewed = LoanApplication.objects.filter(status='hr_reviewed').count()
    total_applications = LoanApplication.objects.count()
    
    recent_applications = LoanApplication.objects.filter(status='guarantor_approved').order_by('-created_at')[:5]
    
    return {
        'pending_applications': pending_applications,
        'hr_reviewed': hr_reviewed,
        'total_applications': total_applications,
        'recent_applications': recent_applications,
    }

def get_loan_officer_dashboard_data():
    pending_applications = LoanApplication.objects.filter(status='hr_reviewed').count()
    loan_officer_reviewed = LoanApplication.objects.filter(status='loan_officer_approved').count()
    total_applications = LoanApplication.objects.count()
    
    recent_applications = LoanApplication.objects.filter(status='hr_reviewed').order_by('-created_at')[:5]
    
    return {
        'pending_applications': pending_applications,
        'loan_officer_reviewed': loan_officer_reviewed,
        'total_applications': total_applications,
        'recent_applications': recent_applications,
    }

def get_committee_dashboard_data():
    pending_applications = LoanApplication.objects.filter(status='loan_officer_approved').count()
    committee_approved = LoanApplication.objects.filter(status='committee_approved').count()
    total_applications = LoanApplication.objects.count()
    
    recent_applications = LoanApplication.objects.filter(status='loan_officer_approved').order_by('-created_at')[:5]
    
    return {
        'pending_applications': pending_applications,
        'committee_approved': committee_approved,
        'total_applications': total_applications,
        'recent_applications': recent_applications,
    }

def get_admin_dashboard_data():
    total_users = User.objects.count()
    total_applications = LoanApplication.objects.count()
    pending_applications = LoanApplication.objects.filter(status='pending').count()
    approved_applications = LoanApplication.objects.filter(status='committee_approved').count()
    
    # Get data for charts
    status_data = {
        'Pending': LoanApplication.objects.filter(status='pending').count(),
        'Guarantor_Approved': LoanApplication.objects.filter(status='guarantor_approved').count(),
        'HR_Reviewed': LoanApplication.objects.filter(status='hr_reviewed').count(),
        'Loan_Officer_Approved': LoanApplication.objects.filter(status='loan_officer_approved').count(),
        'Committee_Approved': LoanApplication.objects.filter(status='committee_approved').count(),
        'Payment_Processing': LoanApplication.objects.filter(status='payment_processing').count(),
        'Disbursed': LoanApplication.objects.filter(status='disbursed').count(),
        'Rejected': LoanApplication.objects.filter(status='rejected').count(),
    }
    
    purpose_data = {}
    for application in LoanApplication.objects.all():
        purpose = application.get_purpose_display()
        purpose_data[purpose] = purpose_data.get(purpose, 0) + 1
    
    # Monthly trends (last 6 months)
    from django.utils import timezone
    from datetime import timedelta
    
    monthly_data = {}
    for i in range(6):
        month = timezone.now() - timedelta(days=30*i)
        month_key = month.strftime('%B %Y')
        monthly_data[month_key] = LoanApplication.objects.filter(
            created_at__month=month.month,
            created_at__year=month.year
        ).count()
    
    # Calculate total loan amount and monthly repayment
    total_loan_amount = LoanApplication.objects.filter(status='committee_approved').aggregate(
        total=Sum('final_approved_amount')
    )['total'] or 0
    
    total_monthly_repayment = LoanApplication.objects.filter(status='committee_approved').aggregate(
        total=Sum('monthly_repayment')
    )['total'] or 0
    
    return {
        'total_users': total_users,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'status_data': status_data,
        'purpose_data': purpose_data,
        'monthly_data': monthly_data,
        'total_loan_amount': total_loan_amount,
        'total_monthly_repayment': total_monthly_repayment,
    }
