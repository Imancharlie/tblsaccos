from django.db import migrations, models
import django.db.models.deletion

def create_default_loan_type(apps, schema_editor):
    LoanType = apps.get_model('loans', 'LoanType')
    LoanApplication = apps.get_model('loans', 'LoanApplication')
    
    # Create a default loan type
    default_loan_type = LoanType.objects.create(
        name='chap_chap',
        max_amount=1000000,
        interest_rate=10.0,
        max_period=1,
        processing_fee=0,
        collateral_required='Hakuna dhamana inayohitajika',
        is_active=True
    )
    
    # Update existing loan applications to use the default loan type
    LoanApplication.objects.update(loan_type=default_loan_type)

def reverse_create_default_loan_type(apps, schema_editor):
    LoanType = apps.get_model('loans', 'LoanType')
    LoanType.objects.filter(name='chap_chap').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0001_initial'),
    ]

    operations = [
        # First create the LoanType model
        migrations.CreateModel(
            name='LoanType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('chap_chap', 'Chap Chap'), ('sikukuu', 'Sikukuu'), ('elimu', 'Elimu'), ('vyombo', 'Vyombo'), ('wanawake', 'Wanawake'), ('dharura', 'Dharura'), ('kupumlia', 'Kupumlia'), ('bima', 'Bima'), ('maendeleo', 'Maendeleo')], max_length=50, unique=True)),
                ('max_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('max_period', models.PositiveIntegerField(help_text='Maximum period in months')),
                ('processing_fee', models.DecimalField(decimal_places=2, default=0, help_text='Processing fee percentage', max_digits=5)),
                ('collateral_required', models.TextField(help_text='Required collateral description')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # Add loan_type field to LoanApplication
        migrations.AddField(
            model_name='loanapplication',
            name='loan_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='loans.loantype'),
        ),
        
        # Run the data migration
        migrations.RunPython(create_default_loan_type, reverse_create_default_loan_type),
        
        # Make loan_type non-nullable
        migrations.AlterField(
            model_name='loanapplication',
            name='loan_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='loans.loantype'),
        ),
        
        # Add new fields to LoanApplication with default values
        migrations.AddField(
            model_name='loanapplication',
            name='borrower_declaration',
            field=models.BooleanField(default=False, help_text='Borrower confirms the declaration'),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='savings_value',
            field=models.DecimalField(decimal_places=2, help_text='Value of savings in TZS', max_digits=12, default=0),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='shares_value',
            field=models.DecimalField(decimal_places=2, help_text='Value of shares', max_digits=12, default=0),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='collateral1_description',
            field=models.CharField(blank=True, help_text='Additional collateral description', max_length=200),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='collateral1_value',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Additional collateral value', max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='collateral2_description',
            field=models.CharField(blank=True, help_text='Additional collateral description', max_length=200),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='collateral2_value',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Additional collateral value', max_digits=12, null=True),
        ),
        
        # Update status choices
        migrations.AlterField(
            model_name='loanapplication',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('guarantor_approved', 'Guarantor Approved'), ('hr_approved', 'HR Approved'), ('loan_officer_approved', 'Loan Officer Approved'), ('committee_approved', 'Committee Approved'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('disbursed', 'Disbursed'), ('completed', 'Completed')], default='pending', max_length=30),
        ),
        
        # Remove salary_slip field
        migrations.RemoveField(
            model_name='loanapplication',
            name='salary_slip',
        ),
        
        # Create HRReview model
        migrations.CreateModel(
            name='HRReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField()),
                ('monthly_salary', models.DecimalField(decimal_places=2, help_text='Borrower monthly salary in TZS', max_digits=12)),
                ('employer_debts', models.DecimalField(decimal_places=2, help_text='Total debts to employer in TZS', max_digits=12)),
                ('financial_debts', models.DecimalField(decimal_places=2, help_text='Total debts to financial institutions in TZS', max_digits=12)),
                ('department_advice', models.TextField(blank=True, help_text='Department advice and comments')),
                ('reviewed_at', models.DateTimeField(auto_now_add=True)),
                ('loan_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hr_reviews', to='loans.loanapplication')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hr_reviews', to='auth.user')),
            ],
        ),
        
        # Create LoanOfficerReview model
        migrations.CreateModel(
            name='LoanOfficerReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField()),
                ('approved_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Final approved amount (can be reduced)', max_digits=12, null=True)),
                ('comments', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(auto_now_add=True)),
                ('loan_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loan_officer_reviews', to='loans.loanapplication')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loan_officer_reviews', to='auth.user')),
            ],
        ),
        
        # Create CommitteeReview model
        migrations.CreateModel(
            name='CommitteeReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField()),
                ('final_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Final committee approved amount', max_digits=12, null=True)),
                ('comments', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(auto_now_add=True)),
                ('loan_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='committee_reviews', to='loans.loanapplication')),
                ('committee_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='committee_reviews', to='auth.user')),
            ],
        ),
        
        # Update GuarantorApproval model
        migrations.AddField(
            model_name='guarantorapproval',
            name='guarantor_declaration',
            field=models.BooleanField(default=False, help_text='Guarantor confirms the declaration'),
        ),
        migrations.AddField(
            model_name='guarantorapproval',
            name='comments',
            field=models.TextField(blank=True),
        ),
        
        # Remove old LoanApproval model
        migrations.DeleteModel(
            name='LoanApproval',
        ),
    ]
