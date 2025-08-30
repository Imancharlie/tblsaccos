from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse

def is_staff(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.user_type in ['hr_officer', 'loan_officer', 'committee_member', 'admin']

def announcement_list(request):
    # Get all announcements (public view)
    announcements = []  # Example: empty for now
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'announcements/announcement_list.html', context)

@login_required
@user_passes_test(is_staff)
def create_announcement(request):
    if request.method == 'POST':
        # Handle announcement creation
        messages.success(request, 'Announcement created successfully!')
        return redirect('announcements:list')
    
    context = {}
    return render(request, 'announcements/create_announcement.html', context)

def announcement_detail(request, pk):
    # Get specific announcement
    announcement = None  # Example: None for now
    
    context = {
        'announcement': announcement,
    }
    return render(request, 'announcements/announcement_detail.html', context)

@login_required
@user_passes_test(is_staff)
def edit_announcement(request, pk):
    # Edit specific announcement
    announcement = None  # Example: None for now
    
    if request.method == 'POST':
        # Handle announcement update
        messages.success(request, 'Announcement updated successfully!')
        return redirect('announcements:detail', pk=pk)
    
    context = {
        'announcement': announcement,
    }
    return render(request, 'announcements/edit_announcement.html', context)

@login_required
@user_passes_test(is_staff)
def delete_announcement(request, pk):
    # Delete specific announcement
    messages.success(request, 'Announcement deleted successfully!')
    return redirect('announcements:list')
