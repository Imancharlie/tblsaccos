from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile, MemberProfile

class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('member', 'Member'),
        ('hr_officer', 'HR Officer'),
        ('loan_officer', 'Loan Officer'),
        ('committee_member', 'Committee Member'),
        ('admin', 'Admin'),
    ]
    
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, initial='member')
    phone_number = forms.CharField(max_length=15, required=False)
    employee_id = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                phone_number=self.cleaned_data['phone_number'],
                employee_id=self.cleaned_data['employee_id'],
                department=self.cleaned_data['department'],
                profile_picture=self.cleaned_data.get('profile_picture')
            )
            # Create MemberProfile if user is a member
            if self.cleaned_data['user_type'] == 'member':
                MemberProfile.objects.create(
                    user=user,
                    bank_name='',
                    account_number='',
                    salary_number='',
                    monthly_salary=0
                )
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ['bank_name', 'account_number', 'salary_number', 'monthly_salary']
        widgets = {
            'monthly_salary': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            try:
                user = User.objects.get(username=username)
                if not user.check_password(password):
                    raise forms.ValidationError("Invalid username or password.")
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid username or password.")
        
        return self.cleaned_data
