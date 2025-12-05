from django.contrib import admin
from .models import *
###################################################################################
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
###################################################################################
@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('type', 'slug')
    search_fields = ('type', 'slug')
    prepopulated_fields = {'slug': ('type',)}
    ordering = ('slug',)
###################################################################################
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published', 'created_at', 'author')
    list_filter = ('published', 'created_at', 'category')
    search_fields = ('title', 'content', 'author', 'meta_keywords')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author', 'published', 'image')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def preview_link(self, obj):
        from django.utils.html import format_html
        return format_html('<a href="{}" target="_blank">Preview</a>', obj.get_absolute_url())
    preview_link.short_description = "Preview"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'short_content', 'created_at', 'active')
    list_filter = ('active', 'created_at', 'blog')
    readonly_fields = ('created_at',)
    actions = ['approve_comments', 'disapprove_comments']

    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = "Content"

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        queryset.update(active=False)
    disapprove_comments.short_description = "Disapprove selected comments"

###################################################################################