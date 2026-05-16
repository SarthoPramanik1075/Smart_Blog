from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from .models import Post, Reaction, Comment
from django.core.mail import send_mail
import random

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PostSerializer


@api_view(['GET'])
def post_list_api(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


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

@login_required
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

    reaction, created = Reaction.objects.get_object_or_create(
        user=request.user,
        post=post,
        default={'reaction_type': reaction_type}
        )
    if not created:
        if reaction.reaction_type == reaction_type:
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