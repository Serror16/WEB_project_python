from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomUserAdmin(UserAdmin):
    """
    Админ
    """
    list_display = ("email", "is_active", "is_staff", "created_at")
    list_filter = ("is_active", "is_staff")
    search_fields = ("email",)
    ordering = ("-created_at",)
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser"),
        }),
        (_("Important dates"), {"fields": ("last_login", "created_at")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )
    
    filter_horizontal = ()
    
    readonly_fields = ("created_at", "last_login")
    
    def get_fieldsets(self, request, obj=None):
        return self.fieldsets


admin.site.register(User, CustomUserAdmin)