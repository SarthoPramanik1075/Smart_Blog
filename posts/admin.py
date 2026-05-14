from django.contrib import admin
from .models import Post, Comment, Reaction

# Register your models here.
# admin.site.register(Post)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'author',
        'created_at'
    ]
    search_fields = ['title']
    list_filter = ['author', 'created_at']
    ordering = ['-created_at'] 

# @admin.register(Comment)
# @admin.register(Reaction)

admin.site.register(Comment)
admin.site.register(Reaction) 