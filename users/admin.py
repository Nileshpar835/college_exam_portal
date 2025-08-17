from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_email_verified', 'is_active')
    list_filter = ('role', 'is_email_verified', 'department', 'is_active')
    actions = ['verify_email_action']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'department', 'is_email_verified')}),
    )
    
    def verify_email_action(self, request, queryset):
        """Admin action to verify email for selected users"""
        updated = queryset.update(is_email_verified=True, is_active=True)
        self.message_user(request, f'{updated} users have been verified.')
    verify_email_action.short_description = "Verify email for selected users"

admin.site.register(CustomUser, CustomUserAdmin)
