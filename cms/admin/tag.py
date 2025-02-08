from django.contrib import admin
from django.utils.translation import gettext_lazy as _

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'view_count')
    list_filter = ('view_count',)
    search_fields = ('name', 'meta_title')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('view_count',)
    save_on_top = True
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Publication Settings'), {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
    )      
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = _('Posts')