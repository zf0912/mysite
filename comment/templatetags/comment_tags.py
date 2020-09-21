# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\comment\templatetags\comment_tags.py
from django import template
from django.contrib.contenttypes.models import ContentType
from comment.models import Comment # 或from ..models import Comment
from comment.forms import CommentForm # 或from ..forms import CommentForm


register= template.Library()	# 用于注册

@register.simple_tag  # 将这个方法注册为simple_tag
def get_comment_count(obj): # 传入obj这个对象，这个对象可以是任意类型。这里我们现在使用的是blog类型
	content_type = ContentType.objects.get_for_model(obj)
	return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count() 

@register.simple_tag
def get_comment_form(obj):
	content_type = ContentType.objects.get_for_model(obj)
	form = CommentForm(initial={
		'content_type': content_type.model, # 取出的content_type是一个对象，加.model取出类型的字符串
		'object_id': obj.pk, 
		'reply_comment_id': 0})
	return form

@register.simple_tag
def get_comment_list(obj):
	content_type = ContentType.objects.get_for_model(obj)
	comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None)
	return comments.order_by('-comment_time')