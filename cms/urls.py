from django.urls import path
from django.contrib.sitemaps.views import sitemap
from .views.post import PostListView, PostDetailView
from .views.category import CategoryView, CategoryListView
from .views.tag import TagView
from .views.pages.page import PageView
from .views.pages.home import HomeView
from .views.pages.contact import ContactView
from .sitemaps import sitemaps
from .feeds import BlogFeed, BlogAtomFeed, CategoryFeed, CategoryAtomFeed

urlpatterns = [
    # Static pages
    path('', HomeView.as_view(), name='home'),
    path('contact/', ContactView.as_view(), name='contact'),
    
    # Post URLs
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/page-<int:page>/', PostListView.as_view(), name='post_list_paginated'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),

    # Category URLs
    path('category/', CategoryListView.as_view(), name='category_list'),
    path('category/page-<int:page>/', CategoryListView.as_view(), name='category_list_paginated'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category_posts'),
    path('category/<slug:slug>/page-<int:page>/', CategoryView.as_view(), name='category_posts_paginated'),
    
    # Tag URLs
    path('tag/<slug:slug>/', TagView.as_view(), name='tagged'),
    path('tag/<slug:slug>/page-<int:page>/', TagView.as_view(), name='tagged_paginated'),

    # **Place feed URLs BEFORE the catch-all page URL**
    path('feed/', BlogFeed(), name='rss_feed'),
    path('feed/atom/', BlogAtomFeed(), name='atom_feed'),
    path('category/<slug:slug>/feed/', CategoryFeed(), name='category_rss_feed'),
    path('category/<slug:slug>/feed/atom/', CategoryAtomFeed(), name='category_atom_feed'),

    # Sitemap URL
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Catch-all Page URLs (must come last)
    path('<slug:slug>/', PageView.as_view(), name='page'),
]