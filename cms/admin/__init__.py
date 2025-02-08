from .category import CategoryAdmin
from .tag import TagAdmin
from .post import PostAdmin
from .page import PageAdmin
from ..models import Category, Tag, Post, Page, SiteSettings
from .settings import SiteSettingsAdmin
from django.contrib import admin

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)