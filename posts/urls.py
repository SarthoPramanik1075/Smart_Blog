from django.urls import path
from .views import (
    add_comment,
    home,
    login_view,
    post_detail,
    create_post,
    delete_post,
    post_list_api,
    react_post,
    update_post,
    register,
    verify_email,
    forget_password,
    reset_password,
    verify_reset_code,
)

urlpatterns = [
    path('', home, name='home'),
    path('post/<int:id>/', post_detail, name='post_detail'),
    path('create/', create_post, name='create_post'),
    path('delete/<int:id>/', delete_post, name='delete_post'),
    path('update/<int:id>/', update_post, name='update_post'),
    path('register/', register, name='register'),
    path('verify_email/', verify_email, name='verify_email'),
    path('login/', login_view, name='login'),
    path('forgot_password/', forget_password, name='forgot_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('verify_reset_code/', verify_reset_code, name='verify_reset_code'),
    path('post/<int:id>/react/<str:reaction_type>/', react_post, name='react_post'),
    path('post/<int:id>/comment/', add_comment, name='add_comment'),
    path('api/posts/', post_list_api, name='post_list_api'),
]