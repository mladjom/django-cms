from cms.views.post import PostListView, PostDetailView
from cms.views.category import CategoryView, CategoryListView
from cms.views.tag import TagView
from cms.views.pages.page import PageView
from cms.views.pages.home import HomeView
from cms.views.pages.contact import ContactView

__all__ = [
    "PostListView",
    "PostDetailView",
    "CategoryView",
    "CategoryListView",
    "TagView",
    "PageView",
    "HomeView",
    "ContactView",
]