from django.contrib import admin
from django.utils.translation import gettext_lazy as _

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