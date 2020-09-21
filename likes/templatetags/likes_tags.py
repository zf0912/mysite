# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\likes\templatetags\likes_tags.py
from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import LikeCount, LikeRecord

register= template.Library()	# 用于注册

@register.simple_tag  # 将这个方法注册为simple_tag
def get_like_count(obj): # 传入obj这个对象，这个对象可以是任意类型。这里我们现在使用的是blog类型
	content_type = ContentType.objects.get_for_model(obj)
	like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=obj.pk)
	return like_count.liked_num

@register.simple_tag(takes_context=True)	# takes_context设置为True，加上之后我们就可以获取到所在模板页面所使用的相关的模板变量,比如获取到user信息
def get_like_status(context, obj):
	content_type = ContentType.objects.get_for_model(obj)
	user = context['user']
	if not user.is_authenticated:
		return ''
	if LikeRecord.objects.filter(content_type=content_type, object_id=obj.pk, user=user).exists():
		return 'active'
	else:
		return ''

# 获取obj这个对象的ContentType类型并返回
@register.simple_tag
def get_content_type(obj):
	content_type = ContentType.objects.get_for_model(obj)
	return content_type.model