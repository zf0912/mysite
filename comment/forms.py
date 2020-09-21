# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\comment\forms.py
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment


class CommentForm(forms.Form):
	content_type = forms.CharField(widget=forms.HiddenInput)	# widget=forms.HiddenInput：隐藏不显示
	object_id = forms.IntegerField(widget=forms.HiddenInput)
	# text = forms.CharField(widget=forms.Textarea)	# 可以输入多行，可换行
	text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'), 
							error_messages={'required': '评论内容不能为空'})
	# 回复的评论对应的主键值	
	reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'reply_comment_id'})) # 设置一个id属性值，可以通过前端页面获取

	def __init__(self, *args, **kwargs):	
	# 传递任意数量的实参和任意数量的关键字实参??   
	# 面向对象的初始化，继承后增加属性的方法？？
	# super方法是类与继承的基础??
	# 给实例一个user属性，相当于改写init方法
		if 'user' in kwargs:
			self.user = kwargs.pop('user') # 参数接收。从kwargs参数中剔除掉'user'这个参数，并赋值给user
		super(CommentForm, self).__init__(*args, **kwargs)

	def clean(self):
		# 上面将user这个对象传进来之后，就可以进行验证
		# 判断用户是否登录
		if self.user.is_authenticated:
			self.cleaned_data['user'] = self.user
		else:
			raise forms.ValidationError('用户尚未登录')

		# 评论对象验证
		content_type = self.cleaned_data['content_type']
		object_id = self.cleaned_data['object_id']
		try:
			model_class = ContentType.objects.get(model=content_type).model_class()
			model_obj = model_class.objects.get(pk=object_id)
			self.cleaned_data['content_object'] = model_obj	# 写入cleaned_data
		except ObjectDoesNotExist:
			raise forms.ValidationError('评论对象不存在')

		return self.cleaned_data

	def clean_reply_comment_id(self):
		reply_comment_id = self.cleaned_data['reply_comment_id']
		if reply_comment_id < 0:
			raise forms.ValidationError('回复出错')
		elif reply_comment_id == 0:	# 顶级评论
			self.cleaned_data['parent'] = None
		elif Comment.objects.filter(pk=reply_comment_id).exists():	# 大于0的时候，判断它在数据库里是否存在
			self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)
		else:
			raise forms.ValidationError('回复出错')
		return reply_comment_id