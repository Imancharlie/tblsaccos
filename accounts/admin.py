from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, MemberProfile, Guarantor, Notification

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    
    def get_user_type(self, obj):
        try:
            return obj.profile.user_type
        except:
            return 'N/A'
    get_user_type.short_description = 'User Type'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank_name', 'monthly_salary', 'total_savings', 'total_shares', 'total_loans', 'total_debts')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'bank_name')
    list_filter = ('created_at', 'updated_at')

@admin.register(Guarantor)
class GuarantorAdmin(admin.ModelAdmin):
    list_display = ('user', 'member', 'savings_amount', 'shares_amount', 'is_approved', 'created_at')
    search_fields = ('user__username', 'member__username')
    list_filter = ('is_approved', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'recipient__first_name', 'recipient__last_name', 'title', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient')
