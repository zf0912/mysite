# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\comment\admin.py
from django.contrib import admin
from .models import Comment

# Register your models here.
@admin.register(Comment) # 注册对应的模型上去
class CommentAdmin(admin.ModelAdmin):
	list_display = ('id', 'content_object', 'text', 'comment_time', 'user', 'root', 'parent')