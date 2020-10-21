# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\my_notifications\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from notifications.models import Notification


def my_notifications(request):
	context = {}
	return render(request, 'my_notifications/my_notifications.html', context)

def my_notification(request, my_notification_pk):
	my_notification = get_object_or_404(Notification, pk=my_notification_pk) # 得到这条消息通知
	my_notification.unread = False	# 得到这个通知之后，将unread改为False
	my_notification.save() # 保存
	return redirect(my_notification.data['url'])	# 重定向，跳转到这条通知的具体url

def delete_my_read_notifications(request):
	notifications = request.user.notifications.read()	# 得到全部已读消息
	notifications.delete()	# 删除
	return redirect(reverse('my_notifications'))	# 重定向到“我的消息”页面