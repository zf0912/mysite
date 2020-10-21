# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\user\signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from notifications.signals import notify


# 用来发送站内消息
@receiver(post_save, sender=User) 
def send_notification(sender, instance, **kwargs): 
	if kwargs['created'] == True:	# 用这个参数来判断是不是第一次创建的用户
		verb = '注册成功，更多精彩内容等你发现'
		url = reverse('user_info')
		notify.send(instance, recipient=instance, verb=verb, action_object=instance, url=url)