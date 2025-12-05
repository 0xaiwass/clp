from django.contrib import admin
from .forms import UserChangeForm, UserCreationForm
from .models import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
#----------------------------------------------------------------------------------------

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('public_id', 'phone', 'email', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active',)
    fieldsets = (
        ('User information', {'fields': ('public_id', 'phone', 'email', 'password')}),
        ('permissions', {'fields': ('is_active', 'is_superuser', 'is_staff', 'last_login')}),
    )
    add_fieldsets = (
        (None, {'fields': ('phone', 'email', 'password1', 'password2')}),
    )
    search_fields = ('email','phone')
    ordering = ('phone', 'email')
    readonly_fields = ('public_id',)
    filter_horizontal = ()


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
#----------------------------------------------------------------------------------------
admin.site.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'created_at')
#----------------------------------------------------------------------------------------
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "province",
        "city",
        "street",
        "postal_code",
        "is_default",
        "created_at",
    )
    list_filter = ("province", "city", "is_default", "created_at")
    search_fields = ("user__username", "user__email", "title", "province", "city", "postal_code")
    ordering = ("-created_at",)
    list_editable = ("is_default",)  # Allow quick edit for default address
    readonly_fields = ("created_at",)

    fieldsets = (
        ("اطلاعات کاربر", {
            "fields": ("user",)
        }),
        ("جزئیات آدرس", {
            "fields": ("title", "province", "city", "street", "postal_code", "is_default")
        }),
        ("سایر", {
            "fields": ("created_at",),
        }),
    )
