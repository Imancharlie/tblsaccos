from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.template.loader import get_template
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import os
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from .models import LoanApplication, GuarantorApproval, HRReview, LoanOfficerReview, CommitteeReview, RepaymentSchedule, LoanType
from .forms import LoanApplicationForm, GuarantorApprovalForm, HRReviewForm, LoanOfficerReviewForm, CommitteeReviewForm
from accounts.models import UserProfile, MemberProfile
from django.db.models import Q
from accounts.models import Notification
from django.contrib.auth.models import User

@login_required
def apply_loan(request):
    if request.method == 'POST':
        print("=== DEBUG: POST request received ===")
        print("POST data:", request.POST)
        print("Files:", request.FILES)
        
        form = LoanApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            print("=== DEBUG: Form is valid ===")
            loan = form.save(commit=False)
            loan.applicant = request.user
            
            # Set a default loan type since it's not in the HTML form
            try:
                default_loan_type = LoanType.objects.filter(is_active=True).first()
                if default_loan_type:
                    loan.loan_type = default_loan_type
                    print(f"DEBUG: Set default loan type: {default_loan_type.name}")
                else:
                    print("DEBUG: No active loan types found!")
                    messages.error(request, 'Hakuna aina ya mkopo inayopatikana. Tafadhali wasiliana na uongozi.')
                    return render(request, 'loans/apply_loan.html', {'form': form})
            except Exception as e:
                print(f"DEBUG: Error setting loan type: {e}")
                messages.error(request, 'Hitilafu katika kuweka aina ya mkopo. Tafadhali jaribu tena.')
                return render(request, 'loans/apply_loan.html', {'form': form})
            
            # Get user profile information
            try:
                profile = request.user.profile
                if not loan.phone_number:
                    loan.phone_number = profile.phone_number
                if not loan.department:
                    loan.department = profile.department
                print(f"DEBUG: User profile data - Phone: {profile.phone_number}, Dept: {profile.department}")
            except Exception as e:
                print(f"DEBUG: Error getting user profile: {e}")
                pass
            
            # Get member profile information
            try:
                member_profile = request.user.member_profile
                if not loan.bank_name:
                    loan.bank_name = member_profile.bank_name
                if not loan.account_number:
                    loan.account_number = member_profile.account_number
                print(f"DEBUG: Member profile data - Bank: {member_profile.bank_name}, Account: {member_profile.account_number}")
            except Exception as e:
                print(f"DEBUG: Error getting member profile: {e}")
                pass
            
            loan.save()
            print(f"DEBUG: Loan saved with ID: {loan.id}")
            
            # Create guarantor approval entries from the new system
            guarantor1_id = request.POST.get('guarantor1_id')
            guarantor2_id = request.POST.get('guarantor2_id')
            guarantor3_id = request.POST.get('guarantor3_id')
            
            print(f"DEBUG: Guarantor IDs - 1: {guarantor1_id}, 2: {guarantor2_id}, 3: {guarantor3_id}")
            
            # Create guarantor approvals
            guarantors_to_create = []
            if guarantor1_id:
                guarantors_to_create.append(guarantor1_id)
            if guarantor2_id:
                guarantors_to_create.append(guarantor2_id)
            if guarantor3_id:
                guarantors_to_create.append(guarantor3_id)
            
            for guarantor_id in guarantors_to_create:
                try:
                    guarantor_user = User.objects.get(id=guarantor_id)
                    GuarantorApproval.objects.create(
                        loan_application=loan,
                        guarantor=guarantor_user
                    )
                    print(f"DEBUG: Created guarantor approval for user ID: {guarantor_id}")
                except User.DoesNotExist:
                    print(f"DEBUG: User with ID {guarantor_id} not found")
                except Exception as e:
                    print(f"DEBUG: Error creating guarantor approval: {e}")
            
            print("DEBUG: Success message set, redirecting...")
            
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Maombi ya mkopo yamewasilishwa kikamilifu!',
                    'redirect_url': reverse('loans:application_detail', kwargs={'pk': loan.pk})
                })
            else:
                messages.success(request, 'Maombi ya mkopo yamewasilishwa kikamilifu!')
                return redirect('loans:application_detail', pk=loan.pk)
        else:
            print("=== DEBUG: Form is NOT valid ===")
            print("Form errors:", form.errors)
            print("Form non-field errors:", form.non_field_errors())
            
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Kuna tatizo katika maombi yako. Tafadhali angalia taarifa zote na jaribu tena.',
                    'errors': form.errors
                })
    else:
        form = LoanApplicationForm()
    
    return render(request, 'loans/apply_loan.html', {'form': form})

@login_required
def application_detail(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user has permission to view this application
    if not (request.user == loan.applicant or 
            hasattr(request.user, 'profile') and request.user.profile.user_type in ['hr_officer', 'loan_officer', 'committee_member', 'admin']):
        messages.error(request, 'Huna ruhusa ya kuona maombi haya.')
        return redirect('loans:tracker')
    
    context = {
        'loan': loan,
        'guarantor_approvals': loan.guarantor_approvals.all(),
        'hr_reviews': loan.hr_reviews.all(),
        'loan_officer_reviews': loan.loan_officer_reviews.all(),
        'committee_reviews': loan.committee_reviews.all(),
        'repayment_schedule': loan.repayment_schedule.all().order_by('installment_number'),
    }
    
    return render(request, 'loans/application_detail.html', context)

@login_required
def application_tracker(request):
    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'member':
        applications = LoanApplication.objects.filter(applicant=request.user).order_by('-created_at')
    else:
        applications = LoanApplication.objects.all().order_by('-created_at')
    
    return render(request, 'loans/application_tracker.html', {'applications': applications})

@login_required
def guarantor_approval(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user is a guarantor for this loan
    try:
        guarantor_approval = loan.guarantor_approvals.get(guarantor=request.user)
    except GuarantorApproval.DoesNotExist:
        messages.error(request, 'Husi mdhamini wa mkopo huu.')
        return redirect('loans:tracker')
    
    if request.method == 'POST':
        form = GuarantorApprovalForm(request.POST, instance=guarantor_approval)
        if form.is_valid():
            approval = form.save(commit=False)
            approval.is_approved = True
            approval.approved_at = timezone.now()
            approval.save()
            
            # Check if all guarantors have approved
            all_approved = all(ga.is_approved for ga in loan.guarantor_approvals.all())
            if all_approved:
                loan.status = 'guarantor_approved'
                loan.guarantor_approval_date = timezone.now()
                loan.save()
                messages.success(request, 'Idhinisho la mdhamini limewasilishwa! Mkopo umeweza kuendelea kwa HR.')
            else:
                messages.success(request, 'Idhinisho la mdhamini limewasilishwa!')
            
            return redirect('loans:application_detail', pk=loan.pk)
    else:
        form = GuarantorApprovalForm(instance=guarantor_approval)
    
    return render(request, 'loans/guarantor_approval.html', {'form': form, 'loan': loan})

@login_required
def hr_review(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user is HR officer
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'hr_officer':
        messages.error(request, 'Huna ruhusa ya kufanya mapitio ya HR.')
        return redirect('staff:hr_workspace')
    
    # Check if loan is ready for HR review
    if loan.status != 'guarantor_approved':
        messages.error(request, 'Mkopo haujafikia hatua ya mapitio ya HR.')
        return redirect('staff:hr_workspace')
    
    if request.method == 'POST':
        form = HRReviewForm(request.POST)
        if form.is_valid():
            # HR review automatically approves the application (just collects information)
            is_approved = True
            
            # Create or update HR review record
            try:
                # Try to get existing HR review record
                hr_review = loan.hr_reviews.first()
                if hr_review:
                    # Update existing record
                    hr_review.monthly_salary = form.cleaned_data['monthly_salary']
                    hr_review.employer_debts = form.cleaned_data['employer_debts']
                    hr_review.financial_debts = form.cleaned_data['financial_debts']
                    hr_review.department_advice = form.cleaned_data['department_advice']
                    hr_review.additional_comments = form.cleaned_data['additional_comments']
                    hr_review.reviewer = request.user
                    hr_review.save()
                else:
                    # Create new record if none exists
                    hr_review = form.save(commit=False)
                    hr_review.loan_application = loan
                    hr_review.reviewer = request.user
                    hr_review.save()
            except Exception as e:
                # Fallback: create new record
                hr_review = form.save(commit=False)
                hr_review.loan_application = loan
                hr_review.reviewer = request.user
                hr_review.save()
            
            # Update loan status and set HR review date
            loan.status = 'hr_reviewed'
            loan.hr_review_date = timezone.now()
            loan.save()
            
            # Automatically create Loan Officer review table with pending status
            from .models import LoanOfficerReview
            LoanOfficerReview.objects.create(
                loan_application=loan,
                officer=None,  # Will be filled when loan officer reviews
                is_approved=None,  # Pending status
                approved_amount=None,
                comments=''
            )
            
            # Notify applicant
            from accounts.views import create_notification
            create_notification(
                recipient=loan.applicant,
                notification_type='loan_status_change',
                title='Loan Status: HR Reviewed',
                message='Mkopo wako umepitia mapitio ya HR. Uko kwenye hatua ya mkopo.',
                related_object_id=loan.id,
                related_object_type='LoanApplication'
            )
            
            messages.success(request, 'Mapitio ya HR yamekamilika! Mkopo umeweza kuendelea kwa Afisa wa Mkopo.')
            return redirect('loans:application_detail', pk=loan.pk)
    else:
        form = HRReviewForm()
    
    return render(request, 'loans/hr_review.html', {'form': form, 'loan': loan})

@login_required
def loan_officer_review(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user is loan officer
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'loan_officer':
        messages.error(request, 'Huna ruhusa ya kufanya mapitio ya afisa wa mkopo.')
        return redirect('loans:tracker')
    
    # Check if loan is ready for loan officer review
    if loan.status != 'hr_reviewed':
        messages.error(request, 'Mkopo haujafikia hatua ya mapitio ya afisa wa mkopo.')
        return redirect('loans:tracker')
    
    if request.method == 'POST':
        form = LoanOfficerReviewForm(request.POST)
        if form.is_valid():
            is_approved = form.cleaned_data['is_approved']
            approved_amount = form.cleaned_data.get('approved_amount')
            
            # Create or update loan officer review record
            try:
                # Try to get existing loan officer review record
                review = loan.loan_officer_reviews.first()
                if review:
                    # Update existing record
                    review.is_approved = form.cleaned_data['is_approved']
                    review.approved_amount = form.cleaned_data.get('approved_amount')
                    review.comments = form.cleaned_data['comments']
                    review.officer = request.user
                    review.save()
                else:
                    # Create new record if none exists
                    review = form.save(commit=False)
                    review.loan_application = loan
                    review.officer = request.user
                    review.save()
            except Exception as e:
                # Fallback: create new record
                review = form.save(commit=False)
                review.loan_application = loan
                review.officer = request.user
                review.save()
            
            # Update loan status
            if is_approved:
                loan.status = 'loan_officer_approved'
                loan.loan_officer_approval_date = timezone.now()
                if approved_amount and approved_amount != loan.amount:
                    loan.final_approved_amount = approved_amount
                    loan.save()  # This will recalculate interest and payments
                
                # Automatically create Committee review table with pending status
                from .models import CommitteeReview
                CommitteeReview.objects.create(
                    loan_application=loan,
                    committee_member=None,  # Will be filled when committee member reviews
                    is_approved=None,  # Pending status
                    final_amount=None,
                    comments=''
                )
                
                # Notify applicant
                from accounts.views import create_notification
                create_notification(
                    recipient=loan.applicant,
                    notification_type='loan_status_change',
                    title='Loan Status: Loan Officer Approved',
                    message='Mkopo wako umepitishwa na afisa wa mkopo. Uko kwenye hatua ya kamati.',
                    related_object_id=loan.id,
                    related_object_type='LoanApplication'
                )
                
                messages.success(request, 'Mapitio ya afisa wa mkopo yamekamilika! Mkopo umeweza kuendelea kwa Kamati.')
            else:
                loan.status = 'rejected'
                
                # Notify applicant of rejection
                from accounts.views import create_notification
                notification_message = f"Your loan application #{loan.id} was rejected by the loan officer."
                create_notification(
                    recipient=loan.applicant,
                    notification_type='loan_rejected',
                    title='Loan Application Rejected',
                    message=notification_message,
                    related_object_id=loan.id,
                    related_object_type='LoanApplication'
                )
                
                messages.warning(request, 'Maombi ya mkopo yamekataliwa.')
            
            loan.save()
            return redirect('loans:application_detail', pk=loan.pk)
    else:
        form = LoanOfficerReviewForm()
    
    return render(request, 'loans/loan_officer_review.html', {'form': form, 'loan': loan})

@login_required
def committee_review(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user is committee member
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'committee_member':
        messages.error(request, 'Huna ruhusa ya kufanya mapitio ya kamati.')
        return redirect('loans:tracker')
    
    # Check if loan is ready for committee review
    if loan.status != 'loan_officer_approved':
        messages.error(request, 'Mkopo haujafikia hatua ya mapitio ya kamati.')
        return redirect('loans:tracker')
    
    if request.method == 'POST':
        form = CommitteeReviewForm(request.POST)
        if form.is_valid():
            is_approved = form.cleaned_data['is_approved']
            final_amount = form.cleaned_data.get('final_amount')
            
            # Create or update committee review record
            try:
                # Try to get existing committee review record
                review = loan.committee_reviews.first()
                if review:
                    # Update existing record
                    review.is_approved = form.cleaned_data['is_approved']
                    review.final_amount = form.cleaned_data.get('final_amount')
                    review.comments = form.cleaned_data['comments']
                    review.committee_member = request.user
                    review.save()
                else:
                    # Create new record if none exists
                    review = form.save(commit=False)
                    review.loan_application = loan
                    review.committee_member = request.user
                    review.save()
            except Exception as e:
                # Fallback: create new record
                review = form.save(commit=False)
                review.loan_application = loan
                review.committee_member = request.user
                review.save()
            
            # Update loan status
            if is_approved:
                loan.status = 'committee_approved'
                loan.committee_approval_date = timezone.now()
                if final_amount and final_amount != loan.amount:
                    loan.final_approved_amount = final_amount
                    loan.save()  # This will recalculate interest and payments
                
                # Automatically create Accountant review table with pending status
                from .models import AccountantReview
                AccountantReview.objects.create(
                    loan_application=loan,
                    accountant=None,  # Will be filled when accountant reviews
                    payment_method='Bank Transfer',
                    bank_details='',
                    processing_notes=''
                )
                
                # Notify applicant
                from accounts.views import create_notification
                create_notification(
                    recipient=loan.applicant,
                    notification_type='loan_status_change',
                    title='Loan Status: Committee Approved',
                    message='Mkopo wako umepitishwa na kamati. Malipo yanashughulikiwa.',
                    related_object_id=loan.id,
                    related_object_type='LoanApplication'
                )
                
                messages.success(request, 'Mapitio ya kamati yamekamilika! Mkopo umekubaliwa! Sasa unangojea malipo.')
            else:
                loan.status = 'rejected'
                
                # Notify applicant of rejection
                from accounts.views import create_notification
                notification_message = f"Your loan application #{loan.id} was rejected by the committee."
                create_notification(
                    recipient=loan.applicant,
                    notification_type='loan_rejected',
                    title='Loan Application Rejected',
                    message=notification_message,
                    related_object_id=loan.id,
                    related_object_type='LoanApplication'
                )
                
                messages.warning(request, 'Maombi ya mkopo yamekataliwa.')
            
            loan.save()
            return redirect('loans:application_detail', pk=loan.pk)
    else:
        form = CommitteeReviewForm()
    
    return render(request, 'loans/committee_review.html', {'form': form, 'loan': loan})

def generate_repayment_schedule(loan):
    """Generate repayment schedule for approved loan"""
    # Clear existing schedule
    loan.repayment_schedule.all().delete()
    
    # Calculate monthly payment
    monthly_payment = loan.monthly_repayment
    start_date = date.today()
    
    for i in range(loan.period):
        due_date = start_date + relativedelta(months=i+1)
        RepaymentSchedule.objects.create(
            loan_application=loan,
            installment_number=i+1,
            due_date=due_date,
            amount=monthly_payment
        )

@login_required
def export_pdf(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user has permission to export this application
    if not (request.user == loan.applicant or 
            hasattr(request.user, 'profile') and request.user.profile.user_type in ['hr_officer', 'loan_officer', 'committee_member', 'admin']):
        messages.error(request, 'Huna ruhusa ya kuhifadhi maombi haya.')
        return redirect('loans:tracker')
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="loan_application_{loan.pk}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#8B0000')  # TBL Maroon
    )
    title = Paragraph("TBL SACCOS Loan Application", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Application Details
    story.append(Paragraph("Application Details", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    details_data = [
        ['Applicant Name:', loan.applicant.get_full_name()],
        ['Loan Type:', loan.loan_type.get_name_display()],
        ['Purpose:', loan.get_purpose_display()],
        ['Amount:', f"TZS {loan.amount:,.2f}"],
        ['Period:', f"{loan.period} months"],
        ['Monthly Repayment:', f"TZS {loan.monthly_repayment:,.2f}"],
        ['Total Interest:', f"TZS {loan.total_interest:,.2f}"],
        ['Total Amount:', f"TZS {loan.total_amount:,.2f}"],
        ['Status:', loan.get_status_display()],
        ['Application Date:', loan.created_at.strftime('%B %d, %Y')],
    ]
    
    details_table = Table(details_data, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#8B0000')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))
    
    # Guarantor Information
    story.append(Paragraph("Guarantor Information", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    guarantors = loan.guarantor_approvals.all()
    if guarantors:
        guarantor_data = [['Guarantor Name', 'Status', 'Declaration']]
        for guarantor in guarantors:
            status = "Approved" if guarantor.is_approved else "Pending"
            declaration = "Yes" if guarantor.guarantor_declaration else "No"
            guarantor_data.append([guarantor.guarantor.get_full_name(), status, declaration])
        
        guarantor_table = Table(guarantor_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        guarantor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(guarantor_table)
    else:
        story.append(Paragraph("No guarantors assigned", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # HR Review Information
    hr_reviews = loan.hr_reviews.all()
    if hr_reviews:
        story.append(Paragraph("HR Review Information", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        hr_data = [['Reviewer', 'Decision', 'Monthly Salary', 'Employer Debts', 'Financial Debts', 'Date']]
        for review in hr_reviews:
            hr_data.append([
                review.reviewer.get_full_name(),
                "Approved" if review.is_approved else "Rejected",
                f"TZS {review.monthly_salary:,.2f}" if review.monthly_salary else "N/A",
                f"TZS {review.employer_debts:,.2f}" if review.employer_debts else "N/A",
                f"TZS {review.financial_debts:,.2f}" if review.financial_debts else "N/A",
                review.reviewed_at.strftime('%B %d, %Y')
            ])
        
        hr_table = Table(hr_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        hr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(hr_table)
        story.append(Spacer(1, 20))
    
    # Approval History
    story.append(Paragraph("Approval History", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Combine all reviews
    all_reviews = []
    for review in loan.loan_officer_reviews.all():
        all_reviews.append(('Loan Officer', review))
    for review in loan.committee_reviews.all():
        all_reviews.append(('Committee', review))
    
    if all_reviews:
        approval_data = [['Approver Type', 'Approver', 'Decision', 'Amount', 'Date', 'Comments']]
        for review_type, review in all_reviews:
            amount = ""
            if hasattr(review, 'approved_amount') and review.approved_amount:
                amount = f"TZS {review.approved_amount:,.2f}"
            elif hasattr(review, 'final_amount') and review.final_amount:
                amount = f"TZS {review.final_amount:,.2f}"
            
            approval_data.append([
                review_type,
                review.reviewer.get_full_name() if hasattr(review, 'reviewer') else review.committee_member.get_full_name(),
                "Approved" if review.is_approved else "Rejected",
                amount,
                review.reviewed_at.strftime('%B %d, %Y'),
                review.comments or "No comments"
            ])
        
        approval_table = Table(approval_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 1.2*inch, 1.2*inch, 2.1*inch])
        approval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(approval_table)
    else:
        story.append(Paragraph("No approvals yet", styles['Normal']))
    
    # Repayment Schedule
    if loan.status == 'committee_approved':
        story.append(Spacer(1, 20))
        story.append(Paragraph("Repayment Schedule", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        schedule = loan.repayment_schedule.all().order_by('installment_number')
        if schedule:
            schedule_data = [['Installment', 'Due Date', 'Amount', 'Status']]
            for installment in schedule:
                status = "Paid" if installment.is_paid else "Pending"
                schedule_data.append([
                    installment.installment_number,
                    installment.due_date.strftime('%B %d, %Y'),
                    f"TZS {installment.amount:,.2f}",
                    status
                ])
            
            schedule_table = Table(schedule_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1*inch])
            schedule_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(schedule_table)
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,  # Center alignment
        textColor=colors.grey
    )
    footer = Paragraph("Generated by TBL SACCOS Loan Management System", footer_style)
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    return response

@login_required
def my_loans(request):
    """View for members to see their loan applications"""
    # if not hasattr(request.user, 'userprofile'):
    #     messages.error(request, 'Huna ruhusa ya kuona ukurasa huu.')
    #     return redirect('dashboard:index')
    
    applications = LoanApplication.objects.filter(applicant=request.user).order_by('-created_at')
    context = {'applications': applications}
    return render(request, 'loans/my_loans.html', context)

@login_required
def make_payment(request, pk):
    """View for making loan payments"""
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user has permission to make payments
    if not (request.user == loan.applicant or 
            hasattr(request.user, 'profile') and request.user.profile.user_type in ['hr_officer', 'loan_officer', 'committee_member', 'admin']):
        messages.error(request, 'Huna ruhusa ya kufanya malipo haya.')
        return redirect('loans:my_loans')
    
    # Check if loan is approved
    if loan.status != 'approved':
        messages.error(request, 'Mkopo haujaruhusiwa bado.')
        return redirect('loans:my_loans')
    
    context = {
        'loan': loan,
    }
    return render(request, 'loans/make_payment.html', context)

@login_required
def payment_history(request, pk):
    """View for viewing loan payment history"""
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user has permission to view payment history
    if not (request.user == loan.applicant or 
            hasattr(request.user, 'profile') and request.user.profile.user_type in ['hr_officer', 'loan_officer', 'committee_member', 'admin']):
        messages.error(request, 'Huna ruhusa ya kuona historia ya malipo.')
        return redirect('loans:my_loans')
    
    context = {
        'loan': loan,
    }
    return render(request, 'loans/payment_history.html', context)

@login_required
def guarantor_requests(request):
    """View for guarantors to see loan requests they need to approve"""
    user = request.user
    
    # Get all loan applications where this user is a guarantor
    # Use the GuarantorApproval model to find applications
    guarantor_requests = LoanApplication.objects.filter(
        guarantor_approvals__guarantor=user
    ).select_related('applicant', 'loan_type').prefetch_related('guarantor_approvals')
    
    # Separate pending and completed requests
    pending_requests = []
    completed_requests = []
    
    for app in guarantor_requests:
        # Check if user has already responded to this application
        user_approval = app.guarantor_approvals.filter(guarantor=user).first()
        
        if user_approval and user_approval.approved_at:  # User has responded
            completed_requests.append({
                'application': app,
                'approval': user_approval,
                'status': 'approved' if user_approval.is_approved else 'rejected'
            })
        else:  # User hasn't responded yet
            pending_requests.append({
                'application': app,
                'approval': user_approval,  # This will be the GuarantorApproval object with is_approved=False
                'status': 'pending'
            })
    
    context = {
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
        'user': user
    }
    
    return render(request, 'loans/guarantor_requests.html', context)

@login_required
def guarantor_approve_reject(request, application_id):
    """View for guarantors to approve or reject loan applications"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    user = request.user
    action = request.POST.get('action')  # 'approve' or 'reject'
    comment = request.POST.get('comment', '')
    
    try:
        application = LoanApplication.objects.get(id=application_id)
        
        # Check if user is actually a guarantor for this application
        if not application.guarantor_approvals.filter(guarantor=user).exists():
            return JsonResponse({'error': 'You are not authorized to approve this application'}, status=403)
        
        # Get the existing guarantor approval record
        guarantor_approval = application.guarantor_approvals.filter(guarantor=user).first()
        
        # Check if user has already responded
        if guarantor_approval and guarantor_approval.approved_at:
            return JsonResponse({'error': 'You have already responded to this application'}, status=400)
        
        # Update the existing guarantor approval record
        if guarantor_approval:
            guarantor_approval.is_approved = (action == 'approve')
            guarantor_approval.comments = comment
            guarantor_approval.approved_at = timezone.now()
            guarantor_approval.save()
        else:
            # This shouldn't happen, but create one if missing
            guarantor_approval = GuarantorApproval.objects.create(
                loan_application=application,
                guarantor=user,
                is_approved=(action == 'approve'),
                comments=comment,
                approved_at=timezone.now()
            )
        
        # Check if all guarantors have responded
        all_guarantors_responded = all(
            ga.approved_at is not None 
            for ga in application.guarantor_approvals.all()
        )
        
        # Check if all responding guarantors approved
        all_approved = all(
            ga.is_approved 
            for ga in application.guarantor_approvals.filter(approved_at__isnull=False)
        )
        
        # Update application status based on guarantor responses
        if all_guarantors_responded:
            if all_approved:
                application.status = 'guarantor_approved'
                application.guarantor_approval_date = timezone.now()
                application.save()
                
                # Automatically create HR review table with pending status
                from .models import HRReview
                HRReview.objects.create(
                    loan_application=application,
                    reviewer=None,  # Will be filled when HR officer reviews
                    monthly_salary=0,
                    employer_debts=0,
                    financial_debts=0,
                    department_advice='',
                    additional_comments=''
                )
                
                # Create notification for applicant
                notification_message = f"All guarantors have approved your loan application #{application.id}. Your application is now being reviewed by HR."
                create_notification(
                    recipient=application.applicant,
                    notification_type='guarantor_response',
                    title='Guarantor Approval Complete',
                    message=notification_message,
                    related_object_id=application.id,
                    related_object_type='LoanApplication'
                )
            else:
                # At least one guarantor rejected
                application.status = 'rejected'
                application.save()
                
                # Create notification for applicant
                notification_message = f"Your loan application #{application.id} was rejected by one or more guarantors."
                create_notification(
                    recipient=application.applicant,
                    notification_type='guarantor_response',
                    title='Loan Application Rejected',
                    message=notification_message,
                    related_object_id=application.id,
                    related_object_type='LoanApplication'
                )
        else:
            # Not all guarantors have responded yet
            notification_message = f"Guarantor {user.get_full_name()} has {'approved' if action == 'approve' else 'rejected'} your loan application #{application.id}. Waiting for other guarantors to respond."
            create_notification(
                recipient=application.applicant,
                notification_type='guarantor_response',
                title='Guarantor Response Received',
                message=notification_message,
                related_object_id=application.id,
                related_object_type='LoanApplication'
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Application {action}d successfully',
            'status': action
        })
        
    except LoanApplication.DoesNotExist:
        return JsonResponse({'error': 'Application not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def search_members(request):
    """API endpoint to search for TBL SACCOS members"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'members': []})
    
    # Search for members by name, employee ID, or department
    members = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(profile__employee_id__icontains=query) |
        Q(profile__department__icontains=query)
    ).filter(
        profile__user_type='member',
        profile__is_active=True
    ).select_related('profile')[:10]  # Limit to 10 results
    
    members_data = []
    for member in members:
        try:
            profile = member.profile
            members_data.append({
                'id': member.id,
                'full_name': member.get_full_name(),
                'employee_id': profile.employee_id or 'N/A',
                'department': profile.department or 'N/A',
                'username': member.username
            })
        except:
            continue
    
    return JsonResponse({'members': members_data})

@login_required
def accountant_review(request, pk):
    """View for accountants to process payment after committee approval"""
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user is accountant or admin
    if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['accountant', 'admin']:
        messages.error(request, 'Huna ruhusa ya kufanya mapitio ya malipo.')
        return redirect('loans:tracker')
    
    # Check if loan is ready for payment processing
    if loan.status != 'committee_approved':
        messages.error(request, 'Mkopo haujafikia hatua ya malipo.')
        return redirect('loans:tracker')
    
    if request.method == 'POST':
        form = AccountantReviewForm(request.POST)
        if form.is_valid():
            # Create or update accountant review record
            try:
                # Try to get existing accountant review record
                accountant_review = loan.accountant_reviews.first()
                if accountant_review:
                    # Update existing record
                    accountant_review.payment_method = form.cleaned_data['payment_method']
                    accountant_review.bank_details = form.cleaned_data['bank_details']
                    accountant_review.processing_notes = form.cleaned_data['processing_notes']
                    accountant_review.accountant = request.user
                    accountant_review.save()
                else:
                    # Create new record if none exists
                    accountant_review = form.save(commit=False)
                    accountant_review.loan_application = loan
                    accountant_review.accountant = request.user
                    accountant_review.save()
            except Exception as e:
                # Fallback: create new record
                accountant_review = form.save(commit=False)
                accountant_review.loan_application = loan
                accountant_review.accountant = request.user
                accountant_review.save()
            
            # Update loan status to payment processing
            loan.status = 'payment_processing'
            loan.payment_processing_date = timezone.now()
            loan.save()
            
            # Notify applicant
            from accounts.views import create_notification
            create_notification(
                recipient=loan.applicant,
                notification_type='loan_status_change',
                title='Loan Status: Payment Processing',
                message='Malipo ya mkopo wako yanashughulikiwa.',
                related_object_id=loan.id,
                related_object_type='LoanApplication'
            )
            
            messages.success(request, 'Malipo yanashughulikiwa! Mkopo umeweza kuendelea kwa hatua ya malipo.')
            return redirect('loans:application_detail', pk=loan.pk)
    else:
        form = AccountantReviewForm()
    
    return render(request, 'loans/accountant_review.html', {'form': form, 'loan': loan})

@login_required
def disburse_loan(request, pk):
    """View for accountants to mark loan as disbursed"""
    loan = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if user is accountant or admin
    if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['accountant', 'admin']:
        messages.error(request, 'Huna ruhusa ya kufanya malipo.')
        return redirect('loans:tracker')
    
    # Check if loan is ready for disbursement
    if loan.status != 'payment_processing':
        messages.error(request, 'Mkopo haujafikia hatua ya malipo.')
        return redirect('loans:tracker')
    
    if request.method == 'POST':
        # Mark loan as disbursed
        loan.status = 'disbursed'
        loan.disbursement_date = timezone.now()
        loan.save()
        
        # Create repayment schedule
        create_repayment_schedule(loan)
        
        # Notify applicant
        from accounts.views import create_notification
        create_notification(
            recipient=loan.applicant,
            notification_type='loan_status_change',
            title='Loan Status: Disbursed',
            message='Mkopo wako umewasilishwa kikamilifu!',
            related_object_id=loan.id,
            related_object_type='LoanApplication'
        )
        
        messages.success(request, 'Mkopo umewasilishwa kikamilifu! Malipo yamefanyika.')
        return redirect('loans:application_detail', pk=loan.pk)
    
    return render(request, 'loans/disburse_loan.html', {'loan': loan})

def check_review_status(loan, review_type):
    """Check if a review table exists and is pending"""
    if review_type == 'hr':
        review = loan.hr_reviews.first()
        return review is not None and review.reviewer is None
    elif review_type == 'loan_officer':
        review = loan.loan_officer_reviews.first()
        return review is not None and review.is_approved is None
    elif review_type == 'committee':
        review = loan.committee_reviews.first()
        return review is not None and review.is_approved is None
    elif review_type == 'accountant':
        review = loan.accountant_reviews.first()
        return review is not None and review.accountant is None
    return False

def get_pending_reviews(loan):
    """Get all pending reviews for a loan application"""
    pending_reviews = []
    
    if check_review_status(loan, 'hr'):
        pending_reviews.append('HR Review')
    if check_review_status(loan, 'loan_officer'):
        pending_reviews.append('Loan Officer Review')
    if check_review_status(loan, 'committee'):
        pending_reviews.append('Committee Review')
    if check_review_status(loan, 'accountant'):
        pending_reviews.append('Accountant Review')
    
    return pending_reviews
