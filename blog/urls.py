from django.urls import path
from .views import posts_list, comments_list, get_post_by_id, get_comment_by_post_id, get_post_by_author, create_post, create_comment
urlpatterns = [
    path('posts/', posts_list, name = 'post_list'),
    path('posts/<int:id>/', get_post_by_id, name = 'get_post_by_id'),
    path('posts/<str:author>/', get_post_by_author, name = 'get_post_by_author'),
    path('posts/<int:post_id>/comments', get_comment_by_post_id, name = 'get_comment_by_post_id'),
    path('posts/create', create_post, name='create_post'),
    path('comments/', comments_list, name = 'comment_list'),
    path('comments/create', create_comment, name = 'create_comment')
]