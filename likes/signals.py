# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\likes\signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import strip_tags
from notifications.signals import notify
from .models import LikeRecord


# 用来发送站内消息
@receiver(post_save, sender=LikeRecord) # 信号接收器，指定由Comment这个模型发送出来，
def send_notification(sender, instance, **kwargs): # 参数：发送者、具体实例（这里对应的是LikeRecord）、额外参数
	if instance.content_type.model == 'blog':
		blog = instance.content_object
		verb = '{0} 点赞了你的 《{1}》'.format(instance.user.get_nickname_or_username(), blog.title)
	elif instance.content_type.model == 'comment':
		comment = instance.content_object
		verb = '{0} 点赞了你的评论“{1}”'.format(
				instance.user.get_nickname_or_username(), 
				strip_tags(comment.text)
			)

	recipient = instance.content_object.get_user()
	url = instance.content_object.get_url()		
	notify.send(instance.user, recipient=recipient, verb=verb, action_object=instance, url=url) 