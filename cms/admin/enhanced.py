from django.contrib import admin
from .mixins import GPT2AdminMixin

class EnhancedModelAdmin(GPT2AdminMixin, admin.ModelAdmin):
    """Base admin class with GPT-2 capabilities"""
    
    class Media:
        js = (
            'admin/js/gpt2_integration.js',  # You'll need to create this
        )
        css = {
            'all': ('admin/css/gpt2_integration.css',)  # You'll need to create this
        }