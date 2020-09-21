# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\comment\urls.py
from django.urls import path
from . import views

urlpatterns = [
	path('update_comment', views.update_comment,  name='update_comment')
]