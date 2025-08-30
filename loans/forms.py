from django import forms
from django.contrib.auth.models import User
from .models import LoanApplication, GuarantorApproval, LoanType, HRReview, LoanOfficerReview, CommitteeReview, AccountantReview

class LoanApplicationForm(forms.ModelForm):
    # Remove guarantor fields since they're handled manually in the HTML
    # guarantor1_id, guarantor2_id, guarantor3_id are handled separately
    
    class Meta:
        model = LoanApplication
        fields = [
            'purpose', 'amount', 'period', 'phone_number', 'department', 
            'bank_name', 'account_number', 'borrower_declaration', 'savings_value', 
            'shares_value', 'collateral1_description', 'collateral1_value', 
            'collateral2_description', 'collateral2_value'
        ]
        widgets = {
            'loan_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '1000', 'class': 'form-control'}),
            'period': forms.NumberInput(attrs={'min': '1', 'max': '60', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter phone number', 'class': 'form-control'}),
            'department': forms.TextInput(attrs={'placeholder': 'Enter department', 'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'placeholder': 'Enter bank name', 'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'placeholder': 'Enter account number', 'class': 'form-control'}),
            'savings_value': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'shares_value': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'collateral1_description': forms.TextInput(attrs={'placeholder': 'Description of additional collateral', 'class': 'form-control'}),
            'collateral1_value': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'collateral2_description': forms.TextInput(attrs={'placeholder': 'Description of additional collateral', 'class': 'form-control'}),
            'collateral2_value': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-fill user data if available
        if 'instance' in kwargs and kwargs['instance']:
            user = kwargs['instance'].applicant
            if user:
                # Try to get user profile data
                try:
                    profile = user.profile
                    if profile.phone_number:
                        self.fields['phone_number'].initial = profile.phone_number
                    if profile.department:
                        self.fields['department'].initial = profile.department
                except:
                    pass
                
                # Try to get member profile data
                try:
                    member_profile = user.member_profile
                    if member_profile.bank_name:
                        self.fields['bank_name'].initial = member_profile.bank_name
                    if member_profile.account_number:
                        self.fields['account_number'].initial = member_profile.account_number
                except:
                    pass

class GuarantorApprovalForm(forms.ModelForm):
    class Meta:
        model = GuarantorApproval
        fields = ['is_approved', 'guarantor_declaration', 'comments']
        widgets = {
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'guarantor_declaration': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
        }

class HRReviewForm(forms.ModelForm):
    class Meta:
        model = HRReview
        fields = ['monthly_salary', 'employer_debts', 'financial_debts', 'department_advice', 'additional_comments']
        widgets = {
            'monthly_salary': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'employer_debts': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'financial_debts': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'department_advice': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'additional_comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Additional HR comments and recommendations'})
        }

class LoanOfficerReviewForm(forms.ModelForm):
    class Meta:
        model = LoanOfficerReview
        fields = ['is_approved', 'approved_amount', 'comments']
        widgets = {
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'approved_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
        }

class CommitteeReviewForm(forms.ModelForm):
    class Meta:
        model = CommitteeReview
        fields = ['is_approved', 'final_amount', 'comments']
        widgets = {
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'final_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
        }

class AccountantReviewForm(forms.ModelForm):
    class Meta:
        model = AccountantReview
        fields = ['payment_method', 'bank_details', 'processing_notes']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Bank Transfer', 'Bank Transfer'),
                ('Mobile Money', 'Mobile Money'),
                ('Cash', 'Cash'),
                ('Check', 'Check')
            ]),
            'bank_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Bank transfer details and account information'}),
            'processing_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Processing notes and comments'})
        }
