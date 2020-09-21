# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\likes\urls.py
from django.urls import path
from . import views

urlpatterns = [
	path('like_change', views.like_change, name='like_change')
]