from django.contrib import admin
from .models import *
###########################################################################################
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "total_price")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        # Prevent adding items manually from admin
        return False
###########################################################################################
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "factor_code",
        "user_phone",
        "paid_status",
        "is_completed",
        "created_at",
        "total_price",
    )
    list_filter = ('id', "paid_status", "is_completed", "created_at")
    search_fields = ("user__phone", "factor_code")
    readonly_fields = ("total_price", "created_at", "factor_code", 'id')
    inlines = [OrderItemInline]

    @admin.display(description="شماره کاربر")
    def user_phone(self, obj):
        return obj.user.phone if hasattr(obj.user, "phone") else "-"

    @admin.display(description="مبلغ کل (تومان)")
    def total_price(self, obj):
        return f"{obj.total_price:,.0f}"
###########################################################################################