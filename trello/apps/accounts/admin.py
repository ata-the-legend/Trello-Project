from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# from trello.apps.accounts.forms import CustomUserCreationForm
from .models import User, UserRecycle

@admin.register(User)
class AppUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "mobile")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "mobile", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("mobile", "first_name", "last_name", "email")
    ordering = ("email",)

    # add_form = CustomUserCreationForm

    actions = ['archive']
    @admin.action(description='Archive Selected Users')
    def archive(self, request, queryset):
        queryset.archive()



@admin.register(UserRecycle)
class UserRecycleAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "mobile", "is_staff")
    actions = ['restore']

    @admin.action(description='Restore Selected Users')
    def restore(self, request, queryset):
        queryset.restore()