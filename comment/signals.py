# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\comment\signals.py
import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from notifications.signals import notify
from .models import Comment


# 用来发送站内消息
@receiver(post_save, sender=Comment) # 信号接收器，指定由Comment这个模型发送出来，
def send_notification(sender, instance, **kwargs): # 参数：发送者、具体实例（这里对应的是comment）、额外参数
	# 发送站内消息
	if instance.reply_to is None: # 如果reply_to是None的话，那么就是评论，否则就是评论
		# 评论
		# 如果是评论的话，需要找到评论的主体（我们这里是博客）
		recipient = instance.content_object.get_user()
		if instance.content_type.model == 'blog':
			blog = instance.content_object
			verb = '{0} 评论了你的 《{1}》'.format(instance.user.get_nickname_or_username(), blog.title)
		else:
			raise Exception('unknow comment object type')
	else:
		# 回复
		recipient = instance.reply_to
		verb = '{0} 回复了你的评论“{1}”'.format(
				instance.user.get_nickname_or_username(), 
				strip_tags(instance.parent.text)
			)
	url = instance.content_object.get_url() + "#commnet_" + str(instance.pk)
	notify.send(instance.user, recipient=recipient, verb=verb, action_object=instance, url=url) 


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

# 用来发送邮件通知
@receiver(post_save, sender=Comment)
def send_email(sender, instance, **kwargs):
	# 发送邮件通知
	# instance.send_mail()

	# 发送邮件通知
	if instance.parent is None:
		# 评论博客的
		subject = '有人评论你的博客'
		email = instance.content_object.get_email()
	else:
		# 回复评论的
		subject = '有人回复你的评论'
		email = instance.reply_to.email
	if email != '':
		context = {}
		context['comment_text'] = instance.text
		context['url'] = instance.content_object.get_url()
		text = render_to_string('comment/send_mail.html', context)
		send_mail = SendMail(subject, text, email)
		send_mail.start()
