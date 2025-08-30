from django.contrib import admin
from .models import (
    LoanType, LoanApplication, GuarantorApproval, 
    HRReview, LoanOfficerReview, CommitteeReview, 
    RepaymentSchedule, LoanPayment, AccountantReview
)

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_amount', 'interest_rate', 'max_period', 'processing_fee', 'is_active']
    list_filter = ['is_active', 'name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'applicant', 'loan_type', 'purpose', 'amount', 'period', 
        'status', 'created_at'
    ]
    list_filter = ['status', 'loan_type', 'purpose', 'created_at']
    search_fields = ['applicant__username', 'applicant__first_name', 'applicant__last_name']
    readonly_fields = ['monthly_repayment', 'total_interest', 'total_amount', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('applicant', 'loan_type', 'purpose', 'amount', 'period', 'status')
        }),
        ('Applicant Details', {
            'fields': ('phone_number', 'department', 'bank_name', 'account_number')
        }),
        ('Declarations and Collateral', {
            'fields': (
                'borrower_declaration', 'savings_value', 'shares_value',
                'collateral1_description', 'collateral1_value',
                'collateral2_description', 'collateral2_value'
            )
        }),
        ('Calculated Fields', {
            'fields': ('monthly_repayment', 'total_interest', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('Workflow Tracking', {
            'fields': (
                'guarantor_approval_date', 'hr_review_date', 'loan_officer_approval_date',
                'committee_approval_date', 'payment_processing_date', 'disbursement_date',
                'final_approved_amount'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(GuarantorApproval)
class GuarantorApprovalAdmin(admin.ModelAdmin):
    list_display = ['loan_application', 'guarantor', 'is_approved', 'guarantor_declaration', 'created_at']
    list_filter = ['is_approved', 'guarantor_declaration', 'created_at']
    search_fields = ['loan_application__applicant__username', 'guarantor__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(HRReview)
class HRReviewAdmin(admin.ModelAdmin):
    list_display = [
        'loan_application', 'reviewer', 
        'monthly_salary', 'reviewed_at'
    ]
    list_filter = ['reviewed_at']
    search_fields = ['loan_application__applicant__username', 'reviewer__username']
    readonly_fields = ['reviewed_at']
    ordering = ['-reviewed_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('loan_application', 'reviewer')
        }),
        ('Financial Assessment', {
            'fields': ('monthly_salary', 'employer_debts', 'financial_debts')
        }),
        ('Department Advice', {
            'fields': ('department_advice', 'additional_comments')
        }),
        ('Timestamps', {
            'fields': ('reviewed_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(LoanOfficerReview)
class LoanOfficerReviewAdmin(admin.ModelAdmin):
    list_display = [
        'loan_application', 'officer', 'is_approved', 
        'approved_amount', 'reviewed_at'
    ]
    list_filter = ['is_approved', 'reviewed_at']
    search_fields = ['loan_application__applicant__username', 'officer__username']
    readonly_fields = ['reviewed_at']
    ordering = ['-reviewed_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('loan_application', 'officer', 'is_approved')
        }),
        ('Amount Adjustment', {
            'fields': ('approved_amount',)
        }),
        ('Comments', {
            'fields': ('comments',)
        }),
        ('Timestamps', {
            'fields': ('reviewed_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(CommitteeReview)
class CommitteeReviewAdmin(admin.ModelAdmin):
    list_display = [
        'loan_application', 'committee_member', 'is_approved', 
        'final_amount', 'reviewed_at'
    ]
    list_filter = ['is_approved', 'reviewed_at']
    search_fields = ['loan_application__applicant__username', 'committee_member__username']
    readonly_fields = ['reviewed_at']
    ordering = ['-reviewed_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('loan_application', 'committee_member', 'is_approved')
        }),
        ('Final Amount', {
            'fields': ('final_amount',)
        }),
        ('Comments', {
            'fields': ('comments',)
        }),
        ('Timestamps', {
            'fields': ('reviewed_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(AccountantReview)
class AccountantReviewAdmin(admin.ModelAdmin):
    list_display = [
        'loan_application', 'accountant', 'payment_method', 'processed_at'
    ]
    list_filter = ['payment_method', 'processed_at']
    search_fields = ['loan_application__applicant__username', 'accountant__username']
    readonly_fields = ['processed_at']
    ordering = ['-processed_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('loan_application', 'accountant', 'payment_method')
        }),
        ('Payment Details', {
            'fields': ('bank_details', 'processing_notes')
        }),
        ('Timestamps', {
            'fields': ('processed_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(RepaymentSchedule)
class RepaymentScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'loan_application', 'installment_number', 'due_date', 
        'amount', 'is_paid', 'paid_at'
    ]
    list_filter = ['is_paid', 'due_date', 'loan_application__status']
    search_fields = ['loan_application__applicant__username']
    readonly_fields = ['paid_at']
    ordering = ['loan_application', 'installment_number']

@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'loan_application', 'amount', 'payment_date', 
        'payment_method', 'reference_number'
    ]
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['loan_application__applicant__username', 'reference_number']
    readonly_fields = ['payment_date']
    ordering = ['-payment_date']
