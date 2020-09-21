# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\blog\urls.py
from django.urls import path
from . import views
'''
http://localhost:8000/blog/1	# 访问具体某篇文章 # http://localhost:8000/blog/	# 博客列表
http://localhost:8000	# 打开首页。总路由
'''

# start with blog
urlpatterns = [
	# http://localhost:8000/blog/
	path('', views.blog_list, name='blog_list'),
	# http://localhost:8000/blog/1
	path('<int:blog_pk>', views.blog_detail, name='blog_detail'),
	# http://localhost:8000/blog/type/1
	path('type/<int:blog_type_pk>', views.blogs_with_type, name='blogs_with_type'), # 这里前面需要加上type/，不然就会和上一条url重复了
	path('date/<int:year>/<int:month>', views.blogs_with_date, name='blogs_with_date'),
]
