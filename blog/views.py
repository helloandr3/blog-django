from rest_framework.decorators import api_view, permission_classes

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from .models import Post, Comment
from django.contrib.auth.models import User
from .serializers import PostSerializer, CommentSerializer, UserSerializer

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiRequest

from django.urls import reverse

##### Users ##### 
@extend_schema(
        request=OpenApiRequest(
            UserSerializer,
            examples=[
                OpenApiExample(
                    name='User Registration Example',
                    value={
                        'username': 'jane_doe',
                        'email': 'jane@example.com',
                        'password': 'StrongPass123'
                    },
                    request_only=True
                )
            ]
        ),
        description='Register new user', responses=UserSerializer(many=True))
@permission_classes([AllowAny])
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

##### Posts ##### 

@extend_schema(description='Retrieve all posts', responses=PostSerializer(many=True))
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def posts_list(request):
    posts = Post.objects.order_by('-created_at')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@extend_schema(description='Retrieve the post with the specified ID', responses=PostSerializer(many=True))
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_post_by_id(request, id):
    try:
        post = Post.objects.get(id=id)
        serialize = PostSerializer(post)
        return Response(serialize.data)
    
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(description='Retrieve all post with the specified author', responses=PostSerializer(many=True))
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_post_by_author(request, author):
    try:
        user = User.objects.get(username=author)
        post = Post.objects.filter(author=user)

        if(post.count() == 0):
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data)
    
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    

@extend_schema(description='Create a new post', request=PostSerializer, responses=PostSerializer)
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_post(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Access denied. User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = PostSerializer(data=request.data)

    if (serializer.is_valid()):
        post = serializer.save(author=request.user)
        headers= {'Location':  reverse('get_post_by_id', args=[post.pk])}
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(description='Update an existing post', request=PostSerializer, responses=PostSerializer)
@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Access denied. User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        post = Post.objects.get(id=post_id)

    except post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PostSerializer(post, data=request.data, partial=True)
    
    if (serializer.is_valid()):
        serializer.save()
        headers= {'Location':  reverse('get_post_by_id', args=[post.pk])}
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(description='Delete the post with the specified ID', request=PostSerializer, responses=PostSerializer)
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Access denied. User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    if post.author is not request.user:
        
        if not request.user.is_superuser:
            return Response({'error': 'Access denied. Only the author or staff can delete a post'}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_staff:
            return Response({'error': 'Access denied. Only the author or staff can delete a post'}, status=status.HTTP_401_UNAUTHORIZED)

    post.delete()
    return Response({'message': f'The post "{post.title}" was successfully deleted'}, status=status.HTTP_200_OK)


##### Comments ##### 

@extend_schema(description='Retrieve all comments from the post with the specified ID', responses=PostSerializer(many=True))
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_comment_by_post_id(request, post_id):
    try:
        comments = Comment.objects.filter(post_id=post_id)

        if(comments.count() == 0):
            return Response({'error': 'Comments not found'}, status=status.HTTP_404_NOT_FOUND)

        serialize =CommentSerializer(comments, many=True)
        return Response(serialize.data)
    
    except Comment.DoesNotExist:
        return Response({'error': 'There is no comment for this post'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(description='Retrieve all comments', responses=PostSerializer(many=True))
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def comments_list(request):
    comments = Comment.objects.order_by('-created_at')
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


@extend_schema(description='Create a new comment', request=CommentSerializer, responses=CommentSerializer)
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_comment(request, post_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Access denied. User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        post = Post.objects.get(id=post_id)

    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CommentSerializer(data=request.data)
    if (serializer.is_valid()):
        serializer.save(author=request.user, post_id=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(description='Delete the comment with the specified ID', request=PostSerializer, responses=PostSerializer)
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_comment(request, comment_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Access denied. User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        comment = Comment.objects.get(id=comment_id)

    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    if comment.author is not request.user:
        
        if not request.user.is_superuser:
            return Response({'error': 'Access denied. Only the author or staff can delete a comment'}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_staff:
            return Response({'error': 'Access denied. Only the author or staff can delete a comment'}, status=status.HTTP_401_UNAUTHORIZED)
   
    comment.delete()
    return Response({'message': f'The comment "{comment.content}" was successfully deleted'}, status=status.HTTP_200_OK)
   