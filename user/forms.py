# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\mysite|user\forms.py
from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

# 登录的表单
class LoginForm(forms.Form):
	# username = forms.CharField(label='用户名', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': '请输入用户名'}))
	username_or_email = forms.CharField(
		label='用户名或邮箱', 
		widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': '请输入用户名或邮箱'})
	)
	password = forms.CharField(
		label='密码', 
		widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请输入密码'})
	)	# PasswordInput是一个类，可以进行实例化，写入一些参数

	# 定义clean方法，清理一些有问题的数据，即等同于views.py里面is_valid()方法的验证行为
	def clean(self):
		# username = self.cleaned_data['username']
		username_or_email = self.cleaned_data['username_or_email']
		password = self.cleaned_data['password']

		# user = auth.authenticate(username=username, password=password)
		user = auth.authenticate(username=username_or_email, password=password)
		if user is None:	# 当获取不到user的时候，就用email进行判断，然后进行登录
			if User.objects.filter(email=username_or_email).exists():	# 判断对应的邮箱是否存在。如果存在，就可以借此获取到用户名，得到user
				username = User.objects.get(email=username_or_email).username
				user = auth.authenticate(username=username, password=password)
				if user:	# 再判断user是否为None，不为None的话，说明验证通过，就可以登录了，记录user信息self.cleaned_data['user'] = user
					self.cleaned_data['user'] = user
					return self.cleaned_data
		# 这边已经进行用户名和密码验证了，但是登录还是要在views.py里的login进行登录，只需要获取user，这个user可以从这边返回过去
		# 所以这里可以把验证之后的user写到clean_data里面，之后返回出来
		else:	# 能获取到user，直接用user登录
			self.cleaned_data['user'] = user
		return self.cleaned_data

# 注册的表单
class RegForm(forms.Form):
	# 构建form
	username = forms.CharField(
		label='用户名',
		max_length=30,
		min_length=3,
		widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': '请输入3-30位用户名'})
	)
	email = forms.EmailField(
		label='邮箱',
		widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': '请输入邮箱'})
	)
	# 验证码
	verification_code = forms.CharField(
		label='验证码', 
		required=False,
		max_length=20,
		widget=forms.TextInput(
			attrs={'class':'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
		)
	)
	password = forms.CharField(
		label='密码',
		min_length=6,
		widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请输入密码'})
	)
	password_again = forms.CharField(
		label='再输入一次密码',
		min_length=6,
		widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '再输入一次密码'})
	)

	# 这段是为了传入request
	def __init__(self, *args, **kwargs):	
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(RegForm, self).__init__(*args, **kwargs)

	def clean(self):
		# 判断验证码
		code = self.request.session.get('register_code', '') # 获取 “为了注册发送的” 验证码
		verification_code = self.cleaned_data.get('verification_code', '')
		if not (code != '' and code == verification_code):
			raise forms.ValidationError('验证码不正确')

		return self.cleaned_data

	# 验证用户名
	def clean_username(self):
		# 获取后需要做一个判断，看是否已存在，如果存在，则不能再注册了
		username = self.cleaned_data['username']
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError('用户名已存在')
		return username

	# 验证邮箱
	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱已存在')
		return email

	# 验证两个密码是否一致
	def clean_password_again(self):
		password = self.cleaned_data['password']
		password_again = self.cleaned_data['password_again']
		if password != password_again:
			raise forms.ValidationError('两次输入的密码不一致')
		return password_again

	# 判断验证码是否为空
	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '').strip()
		if verification_code == '':
			raise forms.ValidationError('验证码不能为空')
		return verification_code

# 修改昵称的表单	
class ChangeNicknameForm(forms.Form):
	nickname_new = forms.CharField(
		label='新的昵称', 
		max_length=20,
		widget=forms.TextInput(
			attrs={'class':'form-control', 'placeholder': '请输入新的昵称'}
		)
	)

	# 验证1：判断用户是否登录
	def __init__(self, *args, **kwargs):	
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super(ChangeNicknameForm, self).__init__(*args, **kwargs)

	def clean(self):
		# 判断用户是否登录
		if self.user.is_authenticated:
			self.cleaned_data['user'] = self.user
		else:
			raise forms.ValidationError('用户尚未登录')
		return self.cleaned_data

	# 验证2：判断提交的昵称是否为空
	def clean_nickname_new(self):
		nickname_new = self.cleaned_data.get('nickname_new', '').strip()
		if nickname_new == '':
			raise ValidationError('新的昵称不能为空')
		return nickname_new

# 绑定邮箱的表单
class BindEmailForm(forms.Form):
	# 表单的两个字段：邮箱+验证码
	# 邮箱
	email = forms.EmailField(
		label='邮箱', 
		widget=forms.EmailInput(
			attrs={'class':'form-control', 'placeholder': '请输入正确的邮箱'}
		)
	)
	# 验证码
	verification_code = forms.CharField(
		label='验证码', 
		required=False,
		max_length=20,
		widget=forms.TextInput(
			attrs={'class':'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
		)
	)

	# 验证1：判断用户是否登录
	def __init__(self, *args, **kwargs):	
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(BindEmailForm, self).__init__(*args, **kwargs)

	def clean(self):
		# 判断用户是否登录
		if self.request.user.is_authenticated:
			self.cleaned_data['user'] = self.request.user
		else:
			raise forms.ValidationError('用户尚未登录')

		# 判断用户是否已绑定邮箱
		if self.request.user.email != '':
			raise forms.ValidationError('你已经绑定邮箱')

		# 判断验证码
		code = self.request.session.get('bind_email_code', '')
		verification_code = self.cleaned_data.get('verification_code', '')
		if not (code != '' and code == verification_code):
			raise forms.ValidationError('验证码不正确')
		return self.cleaned_data

	# 判断邮箱是否已经绑定了，如果绑定了就不能继续绑定
	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('该邮箱已经被绑定')
		return email

	# 判断验证码是否为空
	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '').strip()
		if verification_code == '':
			raise forms.ValidationError('验证码不能为空')
		return verification_code

# 修改密码的表单
class ChangePasswordForm(forms.Form):
	# 三个字段：旧密码、新密码、再输一遍密码
	old_password = forms.CharField(
		label='旧的密码', 
		widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请输入旧的密码'})
	)
	new_password = forms.CharField(
		label='新的密码', 
		widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请输入新的密码'})
	)
	new_password_again = forms.CharField(
		label='请再次输入新的密码', 
		widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请再次输入新的密码'})
	)

	def __init__(self, *args, **kwargs):	
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

	# 验证新的密码是否一致
	def clean(self):
		new_password = self.cleaned_data.get('new_password', '')
		new_password_again = self.cleaned_data.get('new_password_again', '')
		if new_password != new_password_again or new_password == '':
			raise forms.ValidationError('两次输入的密码不一致')
		return self.cleaned_data

	# 验证旧的密码是正确的	
	def clean_old_password(self):
		old_password = self.cleaned_data.get('old_password', '')
		if not self.user.check_password(old_password):
			raise forms.ValidationError('旧的密码错误')
		return old_password

# 忘记密码的表单
class ForgotPasswordForm(forms.Form):
	# 三个字段：邮箱、验证码、新的密码
	email = forms.EmailField(
		label='邮箱',
		widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': '请输入绑定过的邮箱'})
	)
	verification_code = forms.CharField(
		label='验证码', 
		required=False,
		max_length=20,
		widget=forms.TextInput(
			attrs={'class':'form-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
		)
	)
	new_password = forms.CharField(
		label='新的密码', 
		widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '请输入新的密码'})
	)

	def __init__(self, *args, **kwargs):	
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(ForgotPasswordForm, self).__init__(*args, **kwargs)

	# 判断邮箱是否存在
	def clean_email(self):
		email = self.cleaned_data['email'].strip()
		if not User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱不存在')
		return email

	# 判断验证码是否为空
	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '').strip()
		if verification_code == '':
			raise forms.ValidationError('验证码不能为空')

		# 判断验证码是否正确
		code = self.request.session.get('forgot_password_code', '')
		verification_code = self.cleaned_data.get('verification_code', '')
		if not (code != '' and code == verification_code):
			raise forms.ValidationError('验证码不正确')

		return self.cleaned_data
