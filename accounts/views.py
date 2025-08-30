from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, LoginForm, MemberProfileForm
from .models import UserProfile, MemberProfile
from django.http import JsonResponse

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = None
    
    try:
        member_profile = request.user.member_profile
    except MemberProfile.DoesNotExist:
        member_profile = None
    
    if request.method == 'POST':
        # Handle profile picture update
        if 'profile_picture' in request.FILES and user_profile:
            user_profile.profile_picture = request.FILES['profile_picture']
            user_profile.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('accounts:profile')
        
        # Handle member profile update
        if member_profile:
            form = MemberProfileForm(request.POST, instance=member_profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        else:
            form = None
    elif member_profile:
        form = MemberProfileForm(instance=member_profile)
    else:
        form = None
    
    context = {
        'user_profile': user_profile,
        'member_profile': member_profile,
        'form': form,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def settings_view(request):
    """View for user settings page"""
    return render(request, 'accounts/settings.html')

@login_required
def change_password_view(request):
    """View for changing user password"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Check if current password is correct
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:settings')
        
        # Check if new passwords match
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:settings')
        
        # Check password length
        if len(new_password1) < 8:
            messages.error(request, 'New password must be at least 8 characters long.')
            return redirect('accounts:settings')
        
        # Change password
        request.user.set_password(new_password1)
        request.user.save()
        
        messages.success(request, 'Password changed successfully! Please log in again.')
        return redirect('accounts:login')
    
    return redirect('accounts:settings')

@login_required
def update_profile_view(request):
    """View for updating user profile"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        # Update user fields
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        
        # Update profile fields
        try:
            profile = request.user.profile
            profile.phone_number = phone_number
            profile.save()
        except UserProfile.DoesNotExist:
            pass
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:settings')
    
    return redirect('accounts:settings')

@login_required
def update_notifications_view(request):
    """View for updating notification preferences"""
    if request.method == 'POST':
        # This would typically save to a user preferences model
        # For now, just show a success message
        messages.success(request, 'Notification preferences updated successfully!')
        return redirect('accounts:settings')
    
    return redirect('accounts:settings')

@login_required
def notifications(request):
    """View for displaying user notifications"""
    notifications = request.user.notifications.all()[:20]  # Last 20 notifications
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

def get_user_notifications(user):
    """Get user's recent notifications for dashboard"""
    return user.notifications.filter(is_read=False).order_by('-created_at')[:5]

def create_notification(recipient, notification_type, title, message, related_object_id=None, related_object_type=None):
    """Create a new notification"""
    from .models import Notification
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        related_object_id=related_object_id,
        related_object_type=related_object_type
    )
