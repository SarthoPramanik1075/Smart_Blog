from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings
from .models import Post
from django.core.mail import send_mail
import random

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
        
        #create user
        User.objects.create_user(username=username, password=password, email=email)
        #code setup for email verification
        verification_code = random.randint(100000, 999999)
        send_mail(
        'Your Verification Code',
        f'Your verification code is: {verification_code}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

        return redirect('home')
    return render(request, 'posts/register.html')

def post_detail(request, id):
    post=get_object_or_404(Post, id=id)
    return render(request, 'posts/post_detail.html', {'post': post})

def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.user  # Assuming the user is authenticated

        Post.objects.create(title=title, content=content, author=author)
        return redirect('home')
    
    return render(request, 'posts/create_post.html')

def delete_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'posts/delete_post.html', {'post': post})

def update_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()
        return redirect('post_detail', id=post.id)
    return render(request, 'posts/update_post.html', {'post': post})