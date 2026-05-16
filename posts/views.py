from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import PendingRegistration, Post, Reaction, Comment
from django.core.mail import send_mail
import random

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer


def send_code_email(subject, message, email):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER or 'noreply@smartblog.local',
            [email],
            fail_silently=False,
        )
    except Exception as exc:
        print(f'Email sending failed: {exc}')
        print(message)


def serialize_post(request, post):
    return PostSerializer(post, context={'request': request}).data


@api_view(['GET'])
def post_list_api(request):
    posts = Post.objects.prefetch_related('comments', 'reactions').select_related('author')
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@csrf_exempt
@api_view(['POST'])
def register_api(request):
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    confirm_password = request.data.get('confirm_password', '')

    if not username or not email or not password:
        return Response({'detail': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if password != confirm_password:
        return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 8:
        return Response({'detail': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'detail': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    verification_code = random.randint(100000, 999999)
    PendingRegistration.objects.filter(username=username).delete()
    PendingRegistration.objects.filter(email=email).delete()
    PendingRegistration.objects.create(
        username=username,
        email=email,
        password=password,
        verification_code=str(verification_code),
    )
    send_code_email(
        'Your Verification Code',
        f'Your verification code is: {verification_code}',
        email,
    )

    request.session['verification_code'] = str(verification_code)
    request.session['pending_username'] = username
    request.session['pending_email'] = email
    request.session['pending_password'] = password

    return Response(
        {
            'detail': 'Verification code sent. Please verify your email before logging in.',
            'email': email,
        },
        status=status.HTTP_200_OK,
    )


@csrf_exempt
@api_view(['POST'])
def verify_email_api(request):
    entered_code = request.data.get('code', '').strip()
    requested_email = request.data.get('email', '').strip()
    pending = None

    if requested_email:
        pending = PendingRegistration.objects.filter(email=requested_email).first()
    if pending is None:
        session_email = request.session.get('pending_email')
        if session_email:
            pending = PendingRegistration.objects.filter(email=session_email).first()

    if pending is None:
        return Response({'detail': 'No pending registration found. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)
    if entered_code != pending.verification_code:
        return Response({'detail': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=pending.username).exists():
        pending.delete()
        return Response({'detail': 'Username already exists. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=pending.email).exists():
        pending.delete()
        return Response({'detail': 'Email already exists. Please login.'}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(username=pending.username, email=pending.email, password=pending.password)
    pending.delete()

    for key in ['verification_code', 'pending_username', 'pending_email', 'pending_password']:
        request.session.pop(key, None)

    return Response({'detail': 'Email verified successfully. Please login now.'}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
def login_api(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)
    return Response({'id': user.id, 'username': user.username, 'email': user.email})


@csrf_exempt
@api_view(['POST'])
def logout_api(request):
    logout(request)
    return Response({'detail': 'Logged out successfully.'})


@api_view(['GET'])
def me_api(request):
    if not request.user.is_authenticated:
        return Response({'user': None})

    return Response({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        }
    })


@csrf_exempt
@api_view(['GET', 'POST'])
def posts_api(request):
    if request.method == 'GET':
        posts = Post.objects.prefetch_related('comments', 'reactions').select_related('author')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response({'detail': 'Please log in first.'}, status=status.HTTP_401_UNAUTHORIZED)

    title = request.data.get('title', '').strip()
    content = request.data.get('content', '').strip()

    if not title or not content:
        return Response({'detail': 'Title and content are required.'}, status=status.HTTP_400_BAD_REQUEST)

    post = Post.objects.create(title=title, content=content, author=request.user)
    return Response(serialize_post(request, post), status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def post_detail_api(request, id):
    post = get_object_or_404(Post.objects.prefetch_related('comments', 'reactions'), id=id)

    if request.method == 'GET':
        return Response(serialize_post(request, post))

    if not request.user.is_authenticated:
        return Response({'detail': 'Please log in first.'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.user != post.author:
        return Response({'detail': 'Only the author can change this post.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    title = request.data.get('title', '').strip()
    content = request.data.get('content', '').strip()

    if not title or not content:
        return Response({'detail': 'Title and content are required.'}, status=status.HTTP_400_BAD_REQUEST)

    post.title = title
    post.content = content
    post.save()
    return Response(serialize_post(request, post))


@csrf_exempt
@api_view(['POST'])
def comment_api(request, id):
    if not request.user.is_authenticated:
        return Response({'detail': 'Please log in first.'}, status=status.HTTP_401_UNAUTHORIZED)

    post = get_object_or_404(Post, id=id)
    content = request.data.get('content', '').strip()

    if not content:
        return Response({'detail': 'Comment cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

    Comment.objects.create(post=post, author=request.user, content=content)
    post = Post.objects.prefetch_related('comments', 'reactions').get(id=id)
    return Response(serialize_post(request, post), status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
def reaction_api(request, id):
    if not request.user.is_authenticated:
        return Response({'detail': 'Please log in first.'}, status=status.HTTP_401_UNAUTHORIZED)

    post = get_object_or_404(Post, id=id)
    reaction_type = request.data.get('reaction_type', '')
    valid_reactions = [choice[0] for choice in Reaction.Reaction_CHOICES]

    if reaction_type not in valid_reactions:
        return Response({'detail': 'Invalid reaction type.'}, status=status.HTTP_400_BAD_REQUEST)

    reaction, created = Reaction.objects.get_or_create(user=request.user, post=post)
    if not created and reaction.reaction_type == reaction_type:
        reaction.delete()
    else:
        reaction.reaction_type = reaction_type
        reaction.save()

    post = Post.objects.prefetch_related('comments', 'reactions').get(id=id)
    return Response(serialize_post(request, post))


# Create your views here.
def home(request):
    posts = Post.objects.all()
    return render(request, 'posts/home.html', {'posts': posts})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'posts/register.html', {'error': 'Passwords do not match.'})
        if len(password) < 8:
            return render(request, 'posts/register.html', {'error': 'Password must be at least 8 characters long.'})
        if User.objects.filter(username=username).exists():
            return render(request, 'posts/register.html', {'error': 'Username already exists.'})
        if User.objects.filter(email=email).exists():
            return render(request, 'posts/register.html', {'error': 'Email already exists.'})
        
        #code setup for email verification
        verification_code = random.randint(100000, 999999)
        send_mail(
        'Your Verification Code',
        f'Your verification code is: {verification_code}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
        
        request.session['verification_code'] = str(verification_code)
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password

        return redirect('verify_email')
    return render(request, 'posts/register.html')

def verify_email(request):
    if request.method == 'POST':
        entered_code = request.POST['code']
        saved_code = request.session.get('verification_code')
        if entered_code == saved_code:
            username = request.session.get('username')
            email = request.session.get('email')
            password = request.session.get('password')

            User.objects.create_user(username=username, password=password, email=email)
            return redirect('login')
        else:
            return render(request, 'posts/verify_email.html', {'error': 'Invalid verification code.'})
    return render(request, 'posts/verify_email.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user=authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return render(request, 'posts/login.html', {'error': 'Invalid username or password.'})
    return render(request, 'posts/login.html')

def forget_password(request):
    if request.method == 'POST':
        email= request.POST['email']
        if not User.objects.filter(email=email).exists():
            return render(request, 'posts/forget_password.html', {'error': 'Email does not exist.'})

        reset_code = random.randint(100000, 999999)
        request.session['reset_code'] = str(reset_code)
        request.session['reset_email'] = email

        send_mail(
        'Your Password Reset Code',
        f'Your password reset code is: {reset_code}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
        )
        return redirect('reset_password')
    return render(request, 'posts/forget_password.html')

def verify_reset_code(request):

    if request.method == "POST":

        entered_code = request.POST['code']
        saved_code = request.session.get('reset_code')

        if entered_code == saved_code:
            return redirect('reset_password')

        return render(request, 'posts/verify_reset_code.html', {
            'error': 'Invalid reset code'
        })

    return render(request, 'posts/verify_reset_code.html')

def reset_password(request):

    if request.method == "POST":

        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'posts/reset_password.html', {
                'error': 'Passwords do not match'
            })

        if len(password) < 8:
            return render(request, 'posts/reset_password.html', {
                'error': 'Password must be at least 8 characters'
            })

        email = request.session.get('reset_email')

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        # Clear reset session data
        request.session.pop('reset_email', None)
        request.session.pop('reset_code', None)

        return redirect('login')

    return render(request, 'posts/reset_password.html')

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.user  # Assuming the user is authenticated

        Post.objects.create(title=title, content=content, author=author)
        return redirect('home')
    
    return render(request, 'posts/create_post.html')

@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return HttpResponse("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'posts/delete_post.html', {'post': post})

@login_required
def update_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return HttpResponse("You are not allowed to edit this post.")

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()
        return redirect('post_detail', id=post.id)
    return render(request, 'posts/update_post.html', {'post': post})

def post_detail(request, id):
    post=get_object_or_404(Post, id=id)
    return render(request, 'posts/post_detail.html', {'post': post})

@login_required
def react_post(request, id, reaction_type):
    post = get_object_or_404(Post, id=id)

    reaction, created = Reaction.objects.get_or_create(
        user=request.user,
        post=post,
        defaults={'reaction_type': reaction_type}
        )
    if not created:
        if reaction.reaction_type == reaction_type:
            reaction.delete()
        else:
            reaction.reaction_type = reaction_type
            reaction.save()
    return redirect('post_detail', id=id)

@login_required
def add_comment(request, id):

    post = get_object_or_404(Post, id=id)

    if request.method == "POST":
        content = request.POST['content']

        Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )

    return redirect('post_detail', id=post.id)
