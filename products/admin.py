from django.contrib import admin
from .models import *
from django import forms
from django.contrib.contenttypes.admin import GenericTabularInline
#-----------------------------------------------------------
#-----------------------------------------------------------

# Apply RTL to all TextField widgets
class RTLTextArea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {}).update({
            "style": "direction: rtl; text-align: right;",
            "rows": 6,
            "cols": 80,
        })
        super().__init__(*args, **kwargs)

#-----------------------------------------------------------
#-----------------------------------------------------------
class ProductImageInline(GenericTabularInline):
    model = ProductImage
    extra = 3
#-----------------------------------------------------------
#-----------------------------------------------------------

@admin.register(CLP)
class CLPAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'clp_series', 'old_price', 'off_percent',
                    'offer_price', 'is_active', 'is_offer', 'is_new', 'most_selling', 'created_at')

    list_filter = ('clp_series', 'is_active', 'is_offer', 'is_new', 'most_selling', 'created_at')
    search_fields = ('name', 'tags', 'pickup_types',
                     'stick_wood_material', 'fingerboard_wood_material', 'selector_mode', 'bridge')

    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('created_at',)

    class Media:
        css = {
            "all": ("admin/css/dark_ckeditor.css",)
        }

#-----------------------------------------------------------
#-----------------------------------------------------------

@admin.register(AMP)
class AMPAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'type', 'watt', 'panel_screw',
                    'channel_number', 'headphone_output', 'is_active', 'is_offer', 'is_new', 'most_selling', 'created_at')

    list_filter = ('type', 'is_active', 'is_offer', 'is_new', 'most_selling')
    search_fields = ('name', 'tags', 'input', 'output')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('created_at',)

    class Media:
        css = {
            "all": ("admin/css/dark_ckeditor.css",)
        }
#-----------------------------------------------------------
#-----------------------------------------------------------

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = (
        'name', 'equipment_series', 'fret_type', 'neck_type', 'brand',
        'off_percent', 'is_active', 'is_offer', 'is_new', 'most_selling', 'created_at'
    )
    list_filter = ('equipment_series', 'neck_type', 'brand', 'is_active', 'is_offer','most_selling', 'is_new')
    search_fields = ('name', 'tags', 'brand')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('created_at',)

    class Media:
        css = {
            "all": ("admin/css/dark_ckeditor.css",)
        }

#-----------------------------------------------------------
#-----------------------------------------------------------
@admin.register(GuitarStrings)
class GuitarStringsAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = (
        'name', 'string_type', 'tension', 'brand',
        'off_percent', 'is_active', 'is_offer', 'is_new', 'most_selling','created_at'
    )
    list_filter = ('string_type', 'tension', 'brand', 'is_active', 'is_offer', 'most_selling', 'is_new')
    search_fields = ('name', 'tags', 'brand')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('created_at',)

    class Media:
        css = {
            "all": ("admin/css/dark_ckeditor.css",)
        }
#-----------------------------------------------------------
#-----------------------------------------------------------