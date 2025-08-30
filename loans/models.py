from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

class LoanType(models.Model):
    LOAN_TYPES = [
        ('chap_chap', 'Chap Chap'),
        ('sikukuu', 'Sikukuu'),
        ('elimu', 'Elimu'),
        ('vyombo', 'Vyombo'),
        ('wanawake', 'Wanawake'),
        ('dharura', 'Dharura'),
        ('kupumlia', 'Kupumlia'),
        ('bima', 'Bima'),
        ('maendeleo', 'Maendeleo'),
    ]
    
    name = models.CharField(max_length=50, choices=LOAN_TYPES, unique=True)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    max_period = models.PositiveIntegerField(help_text='Maximum period in months')
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Processing fee percentage')
    collateral_required = models.TextField(help_text='Required collateral description')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_name_display()} - Up to {self.max_amount} TZS"
    
    class Meta:
        ordering = ['name']

class LoanApplication(models.Model):
    LOAN_PURPOSES = [
        ('education', 'Education'),
        ('business', 'Business'),
        ('home_improvement', 'Home Improvement'),
        ('debt_consolidation', 'Debt Consolidation'),
        ('emergency', 'Emergency'),
        ('vehicle', 'Vehicle Purchase'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('guarantor_approved', 'Guarantor Approved'),
        ('hr_reviewed', 'HR Reviewed'),
        ('loan_officer_approved', 'Loan Officer Approved'),
        ('committee_approved', 'Committee Approved'),
        ('payment_processing', 'Payment Processing'),
        ('disbursed', 'Disbursed'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    # Basic application details
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications')
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE, related_name='applications')
    purpose = models.CharField(max_length=50, choices=LOAN_PURPOSES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('1000'))])
    period = models.PositiveIntegerField(help_text='Loan period in months', validators=[MinValueValidator(1), MaxValueValidator(60)])
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    # Applicant details
    phone_number = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    
    # Declarations and collateral
    borrower_declaration = models.BooleanField(default=False, help_text='Borrower confirms the declaration')
    savings_value = models.DecimalField(max_digits=12, decimal_places=2, help_text='Value of savings in TZS')
    shares_value = models.DecimalField(max_digits=12, decimal_places=2, help_text='Value of shares')
    collateral1_description = models.CharField(max_length=200, blank=True, help_text='Additional collateral description')
    collateral1_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Additional collateral value')
    collateral2_description = models.CharField(max_length=200, blank=True, help_text='Additional collateral description')
    collateral2_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Additional collateral value')
    
    # Calculated fields
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Workflow tracking fields
    guarantor_approval_date = models.DateTimeField(null=True, blank=True)
    hr_review_date = models.DateTimeField(null=True, blank=True)
    loan_officer_approval_date = models.DateTimeField(null=True, blank=True)
    committee_approval_date = models.DateTimeField(null=True, blank=True)
    payment_processing_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)
    
    # Final approved amount (can be modified by committee)
    final_approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.applicant.get_full_name()} - {self.loan_type.get_name_display()} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if self.amount and self.period and self.loan_type:
            # Calculate based on loan type interest rate
            interest_rate = self.loan_type.interest_rate / Decimal('100')
            period_decimal = Decimal(str(self.period))
            
            if self.loan_type.name == 'wanawake':
                # 1% per month for Wanawake loan
                total_interest = self.amount * Decimal('0.01') * period_decimal
            else:
                # Annual interest rate
                total_interest = self.amount * interest_rate * (period_decimal / Decimal('12'))
            
            self.total_interest = total_interest
            self.total_amount = self.amount + total_interest
            self.monthly_repayment = self.total_amount / period_decimal
            
            # Set final approved amount if not set
            if not self.final_approved_amount:
                self.final_approved_amount = self.amount
        super().save(*args, **kwargs)
    
    def get_workflow_progress(self):
        """Get the current workflow progress percentage"""
        workflow_steps = [
            'pending', 'guarantor_approved', 'hr_reviewed', 
            'loan_officer_approved', 'committee_approved', 
            'payment_processing', 'disbursed'
        ]
        
        try:
            current_step = workflow_steps.index(self.status)
            return int((current_step / (len(workflow_steps) - 1)) * 100)
        except ValueError:
            return 0
    
    def get_current_workflow_step(self):
        """Get the current workflow step description"""
        workflow_steps = {
            'pending': 'Awaiting Guarantor Approval',
            'guarantor_approved': 'Awaiting HR Review',
            'hr_reviewed': 'Awaiting Loan Officer Review',
            'loan_officer_approved': 'Awaiting Committee Review',
            'committee_approved': 'Awaiting Payment Processing',
            'payment_processing': 'Payment Being Processed',
            'disbursed': 'Loan Disbursed',
            'rejected': 'Application Rejected',
            'completed': 'Loan Completed'
        }
        return workflow_steps.get(self.status, 'Unknown Status')
    
    class Meta:
        ordering = ['-created_at']

class GuarantorApproval(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='guarantor_approvals')
    guarantor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guarantor_approvals')
    is_approved = models.BooleanField(default=False)
    guarantor_declaration = models.BooleanField(default=False, help_text='Guarantor confirms the declaration')
    approved_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.guarantor.get_full_name()} - {self.loan_application}"
    
    class Meta:
        unique_together = ['loan_application', 'guarantor']

class HRReview(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='hr_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hr_reviews', null=True, blank=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, help_text='Borrower monthly salary in TZS')
    employer_debts = models.DecimalField(max_digits=12, decimal_places=2, help_text='Total debts to employer in TZS')
    financial_debts = models.DecimalField(max_digits=12, decimal_places=2, help_text='Total debts to financial institutions in TZS')
    department_advice = models.TextField(blank=True, help_text='Department advice and comments')
    additional_comments = models.TextField(blank=True, help_text='Additional HR comments and recommendations')
    reviewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"HR Review - {self.loan_application} by"

class LoanOfficerReview(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='loan_officer_reviews')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_officer_reviews', null=True, blank=True)
    is_approved = models.BooleanField(null=True, blank=True, help_text='True=Approved, False=Rejected, Null=Pending')
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Final approved amount (can be reduced)')
    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Loan Officer Review - {self.loan_application} - {'Approved' if self.is_approved else 'Rejected'}"

class CommitteeReview(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='committee_reviews')
    committee_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='committee_reviews', null=True, blank=True)
    is_approved = models.BooleanField(null=True, blank=True, help_text='True=Approved, False=Rejected, Null=Pending')
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Final committee approved amount')
    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Committee Review - {self.loan_application} - {'Approved' if self.is_approved else 'Rejected'}"

class AccountantReview(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='accountant_reviews')
    accountant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accountant_reviews', null=True, blank=True)
    payment_method = models.CharField(max_length=50, default='Bank Transfer')
    bank_details = models.TextField(blank=True, help_text='Bank transfer details')
    processing_notes = models.TextField(blank=True, help_text='Processing notes and comments')
    processed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Accountant Review - {self.loan_application} by {self.accountant.get_full_name()}"

class RepaymentSchedule(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='repayment_schedule')
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.loan_application} - Installment {self.installment_number}"
    
    class Meta:
        ordering = ['installment_number']

class LoanPayment(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, default='Bank Transfer')
    reference_number = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.loan_application} - {self.amount} - {self.payment_date}"
