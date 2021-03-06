# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\mysite\views.py
# 首页的处理方法
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.cache import cache
from django.core.paginator import Paginator
# from django.contrib import auth
# from django.contrib.auth.models import User
# from django.urls import reverse
# from django.http import JsonResponse

from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data # , get_7_days_hot_data
from notifications.models import Notification
from blog.models import Blog
# from .forms import LoginForm, RegForm

def get_7_days_hot_blogs():
	today = timezone.now().date()
	date = today - datetime.timedelta(days=7)
	blogs = Blog.objects \
				.filter(read_details__date__lt=today, read_details__date__gte=date) \
				.values('id', 'title') \
				.annotate(read_num_sum=Sum('read_details__read_num')) \
				.order_by('-read_num_sum')
	return blogs[:7]

def home(request):
	blog_content_type = ContentType.objects.get_for_model(Blog)
	dates, read_nums = get_seven_days_read_data(blog_content_type)

	# 获取7天热门博客的缓存数据
	hot_blogs_for_7_days = cache.get('hot_blogs_for_7_days')
	if hot_blogs_for_7_days is None:	# 如果为None，则需要进行计算得到缓存数据，这个计算就是get_7_days_hot_blogs()方法
		hot_blogs_for_7_days = get_7_days_hot_blogs()	# 将这个方法写到变量里面，然后进行缓存
		cache.set('hot_blogs_for_7_days', hot_blogs_for_7_days, 3600) # 键值，缓存内容，有效期（这里设置为1h）
	# 	print('calc')
	# else:
	# 	print('use cache')

	context = {}
	context['dates'] = dates
	context['read_nums'] = read_nums
	context['today_hot_data'] = get_today_hot_data(blog_content_type)
	context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
	# context['hot_data_for_7_days'] = get_7_days_hot_data(blog_content_type)
	# context['hot_blogs_for_7_days'] = get_7_days_hot_blogs()
	context['hot_blogs_for_7_days'] = hot_blogs_for_7_days
	return render(request, 'home.html', context)

# 搜索框对应的处理方法
def search(request):
	search_words = request.GET.get('wd', '').strip()	# 获取到wd这个参数
	# 分词：按空格 & | ~
	condition = None
	for word in search_words.split(' '):
		if condition is None:
			condition = Q(title__icontains=word)
		else:
			condition = condition | Q(title__icontains=word)

	search_blogs = []
	if condition is not None:
		# 筛选：搜索	
		# search_blogs = Blog.objects.filter(title__icontains=search_words) # = 全部匹配；__contains= 部分匹配，区分大小写；__icontains= 忽略大小写
		search_blogs = Blog.objects.filter(condition)

	# 分页
	paginator = Paginator(search_blogs, 20)	# 每多少项作为一页
	page_num = request.GET.get('page', 1)	# 获取页码参数（GET请求）。# 看有没有‘page’这个属性，如果没有，则默认给1
	page_of_blogs = paginator.get_page(page_num)

	context = {}
	context['search_words'] = search_words
	context['search_blogs_count'] = search_blogs.count()
	# context['search_blogs'] = search_blogs
	context['page_of_blogs'] = page_of_blogs
	return render(request, 'search.html', context) # 通过render渲染出来，具体渲染页面为search.html，传递的参数是个字典context

'''
def my_notifications(request):
	context = {}
	return render(request, 'my_notifications.html', context)

def my_notification(request, my_notification_pk):
	my_notification = get_object_or_404(Notification, pk=my_notification_pk) # 得到这条消息通知
	my_notification.unread = False	# 得到这个通知之后，将unread改为False
	my_notification.save() # 保存
	return redirect(my_notification.data['url'])	# 重定向，跳转到这条通知的具体url
'''



'''
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
	return render(request, 'login.html', context)

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

	
def register(request):
	if request.method == 'POST':	
		# 实例化
		reg_form = RegForm(request.POST)
		if reg_form.is_valid():
			username = reg_form.cleaned_data['username']
			email = reg_form.cleaned_data['email']
			password = reg_form.cleaned_data['password']
			# 创建用户
			# 方法一：User的create_user方法
			user = User.objects.create_user(username, email, password)
			user.save()
			
			# 方法二：直接用User()实例化，填进去数据
			# user = User()
			# user.username = username
			# user.email = email
			# user.set_password(password)	# 加密后的密码
			# user.save()
			
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
	return render(request, 'register.html', context)

# 登出
def logout(request):
	auth.logout(request)
	return redirect(request.GET.get('from', reverse('home')))

def user_info(request):
	context = {}
	return render(request, 'user_info.html', context)

'''
