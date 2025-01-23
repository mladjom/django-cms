from django.urls import path
from .views import CategoryView, TagView, PostDetailView, PageView, PostListView, CategoryListView

urlpatterns = [
    # Post and Category List URLs
    path('posts/', PostListView.as_view(), name='post_list'),  # List all posts
    path('category/', CategoryListView.as_view(), name='category_list'),
    
    # Category URLs
    path('category/<slug:slug>/', CategoryView.as_view(), name='category_posts'),

    # Tag URLs
    path('tag/<slug:slug>/', TagView.as_view(), name='tagged'),

    # Post Detail URL
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),

    # Page URLs
    path('<slug:slug>/', PageView.as_view(), name='page'),
]