# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\comment\models.py
# import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
# from django.core.mail import send_mail
# from django.conf import settings
# from django.template.loader import render_to_string

'''
class SendMail(threading.Thread):
	""" 封装多线程代码 """

	def __init__(self, subject, text, email, fail_silently=False):	# 初始化，传进来参数
		# 存储传进来的参数，传到属性里边
		self.subject = subject
		self.text = text
		self.email = email
		self.fail_silently = fail_silently
		# 执行本身初始化函数
		threading.Thread.__init__(self)

	def run(self):	# 当执行多线程的时候，会自动执行run里面的代码
		send_mail(
			self.subject, 
			'', 
			settings.EMAIL_HOST_USER, 
			[self.email], 
			fail_silently=self.fail_silently,
			html_message=self.text
		)
'''

class Comment(models.Model):
	# 评论对象。这里我们可以用到前面所讲的ContentType关联任何类型（这里可以复制前面read_statistics里面ReadNum的三个字段）
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	# 评论内容
	text = models.TextField()		# TextField 字段类型，不限字数
	# 评论时间
	comment_time = models.DateTimeField(auto_now_add=True)		# 自动添加时间
	# 评论者。可以关联到django自带的用户系统
	user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
	root = models.ForeignKey('self', related_name="root_comment", null=True, on_delete=models.CASCADE)
	# parent_id= models.IntegerField(default=0)	# 记录上一级是谁的主键值
	parent = models.ForeignKey('self', related_name="parent_comment", null=True, on_delete=models.CASCADE)
	# 指向回复谁
	reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.CASCADE)	# 上面也有一条ForeignKey指向User会报错显示有冲突。原因是：外键关联是双向的

	'''
	def send_mail(self):
		# 发送邮件通知
		if self.parent is None:
			# 评论博客的
			subject = '有人评论你的博客'
			email = self.content_object.get_email()
		else:
			# 回复评论的
			subject = '有人回复你的评论'
			email = self.reply_to.email
		
		# 5个参数为：主题、邮件内容、发送的邮箱（settings中已经设置好了）、要发送到哪个邮箱、发送错误是否抛出错误
		if email != '':
			# text = self.text + '\n' + self.content_object.get_url()	# 反向解析得到链接
			# text = '%s\n<a href="%s">%s</a>' % (self.text + '\n', self.content_object.get_url(), '点击查看')
			context = {}
			context['comment_text'] = self.text
			context['url'] = self.content_object.get_url()
			text = render_to_string('comment/send_mail.html', context)
			# from django.shortcuts import render
			# text = render(None, 'comment/send_mail.html', context).content.decode('utf-8')

			# send_mail(subject, text, settings.EMAIL_HOST_USER, [email], fail_silently=False)
			# 调用多线程方法，开始多线程
			send_mail = SendMail(subject, text, email)
			send_mail.start()
	'''
	
	# 增加一个__str__方法，直接返回评论内容
	def __str__(self):
		return self.text

	def get_url(self):
		return self.content_object.get_url()

	def get_user(self):
		return self.user

	class Meta:
		ordering = ['comment_time']	# 正序排列，-comment_time 是倒序


