from django.urls import path
from .views import (
    home,
    post_detail,
    create_post,
    delete_post,
    update_post,
    register
)

urlpatterns = [
    path('', home, name='home'),
    path('post/<int:id>/', post_detail, name='post_detail'),
    path('create/', create_post, name='create_post'),
    path('delete/<int:id>/', delete_post, name='delete_post'),
    path('update/<int:id>/', update_post, name='update_post'),
    path('register/', register, name='register'),
]