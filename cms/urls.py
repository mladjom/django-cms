from django.urls import path
from django.contrib.sitemaps.views import sitemap
from cms.views.post import PostListView, PostDetailView
from cms.views.category import CategoryView, CategoryListView
from cms.views.tag import TagView
from cms.views.pages.page import PageView
from cms.views.pages.home import HomeView
from cms.views.pages.contact import ContactView
from .sitemaps import sitemaps

urlpatterns = [
    # Home URL
    path('', HomeView.as_view(), name='home'),  
    path('contact/', ContactView.as_view(), name='contact'),  
    # Post and Paginations URLs
    path('posts/', PostListView.as_view(), name='post_list'),  # List all posts
    path('posts/page-<int:page>/', PostListView.as_view(), name='post_list_paginated'),
    # Post Detail URL
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    # Category URLs
    path('category/', CategoryListView.as_view(), name='category_list'),
    path('category/page-<int:page>/', CategoryListView.as_view(), name='category_list_paginated'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category_posts'),
    path('category/<slug:slug>/page-<int:page>/', CategoryView.as_view(), name='category_posts_paginated'),
    # Tag URLs
    path('tag/<slug:slug>/', TagView.as_view(), name='tagged'),
    path('tag/<slug:slug>/page-<int:page>/', TagView.as_view(), name='tagged_paginated'),
    # Page URLs
    path('<slug:slug>/', PageView.as_view(), name='page'),
    # Sitemap URL
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]