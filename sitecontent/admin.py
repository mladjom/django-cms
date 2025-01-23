from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from .models import Category, Tag, Post, Page

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
                   'view_count', 'created_at', 'display_featured_image')
    list_filter = ('status', 'is_featured', 'category', 'author', 'created_at')
    search_fields = ('title', 'content', 'meta_title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    save_on_top = True
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        (_('Media'), {
            'fields': ('featured_image',)
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
    
    def display_featured_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.featured_image.url)
        return ''
    display_featured_image.short_description = _('Image')
    
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
    list_display = ('title', 'view_count')
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
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
    )

