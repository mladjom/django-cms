from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import Category, Tag, Post, Page
from cms.models.admin_notification import AdminNotification

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'view_count', 'display_featured_image')
    list_filter = ('view_count',)
    search_fields = ('name', 'meta_title')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('view_count',)
    save_on_top = True
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = _('Posts')
    
    def display_featured_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.featured_image.url)
        return ''
    display_featured_image.short_description = _('Image')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'view_count')
    list_filter = ('view_count',)
    search_fields = ('name', 'meta_title')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('view_count',)
    save_on_top = True
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = _('Posts')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 
                   'view_count', 'created_at', 'featured_image_preview')
    list_filter = ('status', 'is_featured', 'category', 'author', 'created_at')
    search_fields = ('title', 'content', 'meta_title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'featured_image_preview')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    save_on_top = True
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        (_('Featured Image'), {
            'fields': ('featured_image', 'featured_image_preview'),
        }),
        (_('Categories and Tags'), {
            'fields': ('category', 'tags')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Publication Settings'), {
            'fields': ('status', 'is_featured', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    

    def featured_image_preview(self, obj):
        if obj.featured_image:
            return mark_safe(f'<img src="{obj.featured_image.url}" style="max-width:200px; max-height:200px;" />')
        return 'No Image'
    featured_image_preview.short_description = _('Image Preview')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_at',)
        return self.readonly_fields

    def view_count_display(self, obj):
        return format_html('<b>{}</b>', obj.view_count)
    view_count_display.short_description = _('Views')
    view_count_display.admin_order_field = 'view_count'    
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new post
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'view_count', 'status')
    search_fields = ('title', 'content', 'meta_title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count',)
    save_on_top = True
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'content')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('view_count', 'status'), 
            'classes': ('collapse',)
        }),
    )

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'level_badge', 'created_at', 'expires_at', 'recipient_count', 'is_read')
    list_filter = ('level', 'is_read', 'created_at', 'expires_at')
    search_fields = ('title', 'message', 'recipients__username', 'recipients__email')
    readonly_fields = ('created_at',)
    filter_horizontal = ('recipients',)
    save_on_top = True
   
    def level_badge(self, obj):
        colors = {
            'info': 'blue',
            'warning': 'orange',
            'error': 'red'
        }
        color = colors.get(obj.level, 'gray')  # Default to 'gray' if level is not found
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_level_display()
        )
    level_badge.short_description = _('Level')

    def recipient_count(self, obj):
        return obj.recipients.count()
    recipient_count.short_description = _('Number of Recipients')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('recipients')

    fieldsets = (
        (None, {
            'fields': ('title', 'message', 'level')
        }),
        (_('Recipients'), {
            'fields': ('recipients',)
        }),
        (_('Timing'), {
            'fields': ('created_at', 'expires_at')
        }),
        (_('Status'), {
            'fields': ('is_read',)
        })
    )