# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\mysite\models.py
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE) # 创建外键，与User关联。一对一字段，一个Profile对应一个User，一个User对应一个Profile
	nickname = models.CharField(max_length=20, verbose_name='昵称')

	def __str__(self):	# 显示字符串
		return '<Profile: %s for %s>' % (self.nickname, self.user.username)

# 获取昵称
def get_nickname(self):
	if Profile.objects.filter(user=self).exists():
		profile = Profile.objects.get(user=self)
		return profile.nickname
	else:
		return ''

# 获取昵称或者用户名（有昵称，则获取昵称，没有，则获取用户名）
def get_nickname_or_username(self):
	if Profile.objects.filter(user=self).exists():
		profile = Profile.objects.get(user=self)
		return profile.nickname
	else:
		return self.username

# 判断有无昵称
def has_nickname(self):
	return Profile.objects.filter(user=self).exists()

# 动态绑定
User.get_nickname = get_nickname # User创建一个属性get_nickname，将上面的get_nickname方法作为一个值，赋值给这个属性
User.get_nickname_or_username = get_nickname_or_username
User.has_nickname = has_nickname


