# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\read_statistics\admin.py
from django.contrib import admin
from .models import ReadNum, ReadDetail

@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
	list_display = ('read_num', 'content_object')	# models.py中的ReadNum的read_num、content_object（content_object包括了'content_type', 'object_id'）

@admin.register(ReadDetail)
class ReadDetailAdmin(admin.ModelAdmin):
	list_display = ('date', 'read_num', 'content_object')