from django.contrib import admin
from .models import *
##############################################################################
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'total_price')
    fields = ('product', 'quantity', 'total_price')
    can_delete = True
##############################################################################
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_code', 'user', 'created_at', 'total_price_display')
    search_fields = ('user__phone', 'id')
    inlines = [CartItemInline]
    readonly_fields = ('total_price_display', "created_at", "cart_code", 'id')


    @admin.display(description="مبلغ کل (تومان)")
    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"
    total_price_display.short_description = "مبلغ کل"
##############################################################################