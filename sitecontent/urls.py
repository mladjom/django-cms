from django.urls import path
from django.contrib.sitemaps.views import sitemap
from .views import HomeView, CategoryView, TagView, PostDetailView, PageView, PostListView, CategoryListView
from .sitemaps import sitemaps

urlpatterns = [
    # Home URL
    path('', HomeView.as_view(), name='home'),  
    # Post and Paginations URLs
    path('posts/', PostListView.as_view(), name='post_list'),  # List all posts
    path('posts/page-<int:page>/', PostListView.as_view(), name='post-list'),
    # Post Detail URL
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    # Category URLs
    path('category/', CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category_posts'),
    # Tag URLs
    path('tag/<slug:slug>/', TagView.as_view(), name='tagged'),
    # Page URLs
    path('<slug:slug>/', PageView.as_view(), name='page'),
    # Sitemap URL
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]