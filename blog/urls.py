from django.urls import path
from .views import posts_list, comments_list, get_post_by_id, get_comment_by_post_id, get_post_by_author, create_post, create_comment, update_post, delete_post, delete_comment
urlpatterns = [
    # posts
    path('posts/', posts_list, name = 'post_list'),
    path('posts/<int:id>/', get_post_by_id, name = 'get_post_by_id'),
    path('posts/author/<str:author>/', get_post_by_author, name = 'get_post_by_author'),
    path('posts/create', create_post, name='create_post'),
    path('posts/<int:post_id>/', update_post, name='update_post'),
    path('posts/<int:post_id>/', delete_post, name='delete_post'),

    # comments
    path('comments/', comments_list, name = 'comment_list'),
    path('comments/posts/<int:post_id>/', get_comment_by_post_id, name = 'get_comment_by_post_id'),
    path('comments/create', create_comment, name = 'create_comment'),
    path('comments/<int:comment_id>/', delete_comment, name = 'delete_comment')
]