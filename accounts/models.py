from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('member', 'Member'),
        ('hr_officer', 'HR Officer'),
        ('loan_officer', 'Loan Officer'),
        ('committee_member', 'Committee Member'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='member')
    phone_number = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    salary_number = models.CharField(max_length=50)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_shares = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_loans = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_debts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Profile"
    
    @property
    def available_balance(self):
        return self.total_savings + self.total_shares - self.total_loans - self.total_debts
    
    @property
    def loan_eligibility(self):
        # Basic eligibility: savings + shares should be at least 20% of requested loan
        return self.available_balance > 0

class Guarantor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guarantor_for')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guarantors')
    savings_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shares_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} guarantees {self.member.get_full_name()}"
    
    @property
    def total_guarantee(self):
        return self.savings_amount + self.shares_amount

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('guarantor_request', 'Guarantor Request'),
        ('hr_review_pending', 'HR Review Pending'),
        ('loan_officer_review_pending', 'Loan Officer Review Pending'),
        ('committee_review_pending', 'Committee Review Pending'),
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
        ('payment_due', 'Payment Due'),
        ('general', 'General Update'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.get_notification_type_display()}"
    
    @property
    def is_unread(self):
        return not self.is_read
