# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\user\views.py
import string
import random
import time
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from .models import Profile


def login_for_modal(request):
	# 这里是POST请求，不用去验证
	login_form = LoginForm(request.POST)
	data = {}
	if login_form.is_valid():	# 如果有效，说明验证通过
		user = login_form.cleaned_data['user']
		auth.login(request, user)
		data['status'] = 'SUCCESS'
	else:
		data['status'] = 'ERROR'
	return JsonResponse(data)

def login(request):
	# 1）如果请求方式是POST的话，则是提交数据行为
	if request.method == 'POST':	
		# 2）提交数据部分。需要验证提交的数据是否有效
		# 3）先接收数据，实例化
		login_form = LoginForm(request.POST) # 将提交的数据 初始化一下
		# 4）判断数据是否有效
		if login_form.is_valid():	# 如果有效，说明验证通过
			user = login_form.cleaned_data['user']
			auth.login(request, user)
			return redirect(request.GET.get('from', reverse('home')))
	# 其他行为，则是加载页面
	else:	
		# 实例化
		login_form = LoginForm() 
	# 创建前端页面
	context = {}
	context['login_form'] = login_form
	return render(request, 'user/login.html', context)
	
def register(request):
	if request.method == 'POST':	
		# 实例化
		reg_form = RegForm(request.POST, request=request)
		if reg_form.is_valid():
			username = reg_form.cleaned_data['username']
			email = reg_form.cleaned_data['email']
			password = reg_form.cleaned_data['password']
			# 创建用户
			# 方法一：User的create_user方法
			user = User.objects.create_user(username, email, password)
			user.save()

			# 清除session
			del request.session['register_code']

			# 登录用户
			user = auth.authenticate(username=username, password=password)	# 直接登录是有效的，因为用户名和密码是刚刚创建的
			auth.login(request, user)
			# 跳转
			return redirect(request.GET.get('from', reverse('home')))
	else:	
		# 实例化
		reg_form = RegForm() 
	# 创建前端页面
	context = {}
	context['reg_form'] = reg_form
	return render(request, 'user/register.html', context)

def logout(request):
	auth.logout(request)
	return redirect(request.GET.get('from', reverse('home')))

def user_info(request):
	context = {}
	return render(request, 'user/user_info.html', context)

def change_nickname(request):
	redirect_to = request.GET.get('from', reverse('home'))

	if request.method == 'POST':
		form = ChangeNicknameForm(request.POST, user=request.user)	# 获取form表单
		if form.is_valid():	# 对是否合理进行判断。这里我们需要判断两个东西：提交的新昵称是否为空、是否登录了（回到forms.py进行修改）
			nickname_new = form.cleaned_data['nickname_new']
			profile, created = Profile.objects.get_or_create(user=request.user)
			profile.nickname = nickname_new
			profile.save()
			# 修改昵称保存之后，跳转到之前的页面
			return redirect(redirect_to)
	else:
		form = ChangeNicknameForm()
	context = {}
	context['page_title'] = '修改昵称'
	context['form_title'] = '修改昵称'
	context['submit_text'] = '修改'
	context['form'] = form
	context['return_back_url'] = redirect_to
	return render(request, 'form.html', context)

def bind_email(request):
	redirect_to = request.GET.get('from', reverse('home'))

	if request.method == 'POST':
		# form = BindEmailForm(request.POST, user=request.user)	# 获取form表单
		form = BindEmailForm(request.POST, request=request)	# 获取form表单
		if form.is_valid():
			email = form.cleaned_data['email']
			request.user.email = email
			request.user.save()

			# 清除session
			del request.session['bind_email_code']

			return redirect(redirect_to)
	else:
		form = BindEmailForm()
	context = {}
	context['page_title'] = '绑定邮箱'
	context['form_title'] = '绑定邮箱'
	context['submit_text'] = '绑定'
	context['form'] = form
	context['return_back_url'] = redirect_to
	return render(request, 'user/bind_email.html', context)

def send_verification_code(request):
	email = request.GET.get('email', '')
	# 发送是为了干嘛
	send_for = request.GET.get('send_for', '') 

	data = {}

	if email != '':
		# 生成验证码
		code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
		
		now = int(time.time())	# 当前时间
		send_code_time = request.session.get('send_code_time', 0)
		if now - send_code_time < 30:
			data['status'] = 'ERROR'
		else:
			# 保存发送的验证码code和发送的时间now
			# request.session['bind_email_code'] = code	# 将验证码存起来。session是服务器，可以存储user相关的一些数据，key为绑定邮箱储存对应的验证码 value为验证码code，session具有有效期
			request.session[send_for] = code
			request.session['send_code_time'] = now	

			# 发送邮件
			send_mail(
			    '绑定邮箱',
			    '验证码： %s' % code,
			    '1248285187@qq.com',
			    [email],
			    fail_silently=False,
			)
			data['status'] = 'SUCCESS'

	else:
		data['status'] = 'ERROR'
	return JsonResponse(data)

def change_password(request):
	redirect_to = reverse('home')

	if request.method == 'POST':
		form = ChangePasswordForm(request.POST, user=request.user)	# 获取form表单
		if form.is_valid():
			user = request.user
			old_password = form.cleaned_data['old_password']
			new_password = form.cleaned_data['new_password']
			user.set_password(new_password)
			user.save()
			auth.logout(request)
			return redirect(redirect_to)
	else:
		form = ChangePasswordForm()

	context = {}
	context['page_title'] = '修改密码'
	context['form_title'] = '修改密码'
	context['submit_text'] = '修改'
	context['form'] = form
	context['return_back_url'] = redirect_to
	return render(request, 'form.html', context)

def forgot_password(request):
	redirect_to = reverse('login')

	if request.method == 'POST':
		form = ForgotPasswordForm(request.POST, request=request) # 获取form表单
		if form.is_valid():	# 验证通过，重置密码
			email = form.cleaned_data['email']
			new_password = form.cleaned_data['new_password']
			user = User.objects.get(email=email)
			user.set_password(new_password)
			user.save()
			# 清除session
			del request.session['forgot_password_code']

			return redirect(redirect_to)
	else:
		form = ForgotPasswordForm()
	context = {}
	context['page_title'] = '重置密码'
	context['form_title'] = '重置密码'
	context['submit_text'] = '重置'
	context['form'] = form
	context['return_back_url'] = redirect_to
	return render(request, 'user/forgot_password.html', context)