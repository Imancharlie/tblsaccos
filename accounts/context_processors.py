def user_type_processor(request):
    """Context processor to make user_type available in all templates"""
    if request.user.is_authenticated:
        try:
            user_type = request.user.profile.user_type
        except Exception as e:
            user_type = 'member'  # Default fallback
    else:
        user_type = None
    
    return {
        'user_type': user_type,
        'is_member': user_type == 'member',
        'is_hr_officer': user_type == 'hr_officer',
        'is_loan_officer': user_type == 'loan_officer',
        'is_committee_member': user_type == 'committee_member',
        'is_admin': user_type == 'admin',
    }


def notifications_processor(request):
    """Context processor to provide notification data globally"""
    if request.user.is_authenticated:
        try:
            unread_count = request.user.notifications.filter(is_read=False).count()
        except Exception as e:
            # Log the error for debugging
            print(f"Error in notifications_processor: {e}")
            unread_count = 0
    else:
        unread_count = 0
    
    return {
        'unread_notifications_count': unread_count
    }


def guarantor_requests_processor(request):
    """Context processor to provide guarantor requests count globally"""
    if request.user.is_authenticated:
        try:
            from loans.models import LoanApplication
            from django.db.models import Q
            
            # Count pending guarantor requests for this user
            guarantor_count = LoanApplication.objects.filter(
                Q(guarantor_approvals__guarantor=request.user) & 
                Q(guarantor_approvals__approved_at__isnull=True)
            ).distinct().count()
        except Exception as e:
            # Log the error for debugging
            print(f"Error in guarantor_requests_processor: {e}")
            guarantor_count = 0
    else:
        guarantor_count = 0
    
    return {
        'guarantor_requests_count': guarantor_count
    }


def pending_payments_processor(request):
    """Context processor to provide pending payments count for accountants"""
    if request.user.is_authenticated:
        try:
            from loans.models import LoanApplication
            
            # Count pending payments for accountants (loans approved by committee)
            if hasattr(request.user, 'profile') and request.user.profile.user_type in ['accountant', 'admin']:
                pending_payments = LoanApplication.objects.filter(status='committee_approved').count()
            else:
                pending_payments = 0
        except Exception as e:
            # Log the error for debugging
            print(f"Error in pending_payments_processor: {e}")
            pending_payments = 0
    else:
        pending_payments = 0
    
    return {
        'pending_payments': pending_payments
    }


def pending_applications_processor(request):
    """Context processor to provide pending applications count for staff"""
    pending_count = 0  # Initialize default value
    
    if request.user.is_authenticated:
        try:
            from loans.models import LoanApplication
            
            if hasattr(request.user, 'profile'):
                user_type = request.user.profile.user_type
                
                if user_type == 'hr_officer':
                    # HR officers see guarantor-approved applications
                    pending_count = LoanApplication.objects.filter(status='guarantor_approved').count()
                elif user_type == 'loan_officer':
                    # Loan officers see HR-reviewed applications
                    pending_count = LoanApplication.objects.filter(status='hr_reviewed').count()
                elif user_type == 'committee_member':
                    # Committee members see loan officer approved applications
                    pending_count = LoanApplication.objects.filter(status='loan_officer_approved').count()
                # else: pending_count remains 0 (default)
        except Exception as e:
            # Log the error for debugging
            print(f"Error in pending_applications_processor: {e}")
            pending_count = 0  # Reset to 0 on error
    
    return {
        'pending_applications': pending_count
    }


