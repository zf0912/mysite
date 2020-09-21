# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\blog\views.py
from django.shortcuts import get_object_or_404, render # render_to_response # render_to_response:用模板页面输出响应内容
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType

from .models import Blog, BlogType
from read_statistics.utils import read_statistics_once_read
# from mysite.forms import LoginForm
# from user.forms import LoginForm

def get_blog_list_common_data(request, blogs_all_list):
	paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)	# 每多少篇博客作为一页
	page_num = request.GET.get('page', 1)	# 获取页码参数（GET请求）。# 看有没有‘page’这个属性，如果没有，则默认给1
	page_of_blogs = paginator.get_page(page_num)	# 这里get_page方法，如果获取到的是其他字符而不是整数数字，会自动转化为1，使得它是处于有效的范围内
	current_page_num = page_of_blogs.number # 获取当前页码
	# 获取当前页码前后各2页的页码范围
	page_range = list(range(max(current_page_num-2, 1), min(current_page_num+3, paginator.num_pages+1)))
	
	# 先加上省略页码标记
	if page_range[0] - 1 >= 2:
		page_range.insert(0, '...')
	if paginator.num_pages - page_range[-1] >= 2:
		page_range.append('...')
	# 然后加上首页和尾页
	if page_range[0] != 1:
		page_range.insert(0, 1)
	if page_range[-1] != paginator.num_pages:
		page_range.append(paginator.num_pages)

	# 获取博客分类的对应博客数量
	# BlogType.objects.annotate(blog_count=Count('blog'))	# 参数是外键相关联对象的名称的小写
	# （当然，如果想要明确一点的话，也可以在models.py中blog_type后加上related_name='blog_blog'，然后这里的参数就可以通过blog_blog来关联
	'''
	blog_types = BlogType.objects.all()
	blog_types_list = []
	for blog_type in blog_types:
		blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()	# 等号左边是参数名，右边是参数值
		blog_types_list.append(blog_type)
	'''

	# 获取日期归档对应的博客数量
	blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
	blog_dates_dict ={}
	for blog_date in blog_dates:
		blog_count = Blog.objects.filter(created_time__year=blog_date.year, created_time__month=blog_date.month).count()
		blog_dates_dict[blog_date] = blog_count

	context = {}
	context['blogs'] = page_of_blogs.object_list
	context['page_of_blogs'] = page_of_blogs	# 修改。返回具体的博客给前端模板页面
	context['page_range'] = page_range
	# 获取博客分类的对应博客数量
	# context['blog_types'] = BlogType.objects.all()
	# context['blog_types'] = blog_types_list
	context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))	# 参数是外键相关联对象的名称的小写
	# （当然，如果想要明确一点的话，也可以在models.py中blog_type后加上related_name='blog_blog'，然后这里的参数就可以通过blog_blog来关联
	
	# 获取日期归档对应的博客数量
	# context['blog_dates'] = Blog.objects.dates('created_time', 'month', order='DESC') 
	context['blog_dates'] = blog_dates_dict
	return context

# 需要两个处理方法：1.访问博客列表；2.显示具体的blog页面
def blog_list(request):
	blogs_all_list = Blog.objects.all()	# 获取所有博客
	context = get_blog_list_common_data(request, blogs_all_list)
	return render(request, "blog/blog_list.html", context)

# 处理分类博客的页面的方法——按照博客类型分类
def blogs_with_type(request, blog_type_pk):
	blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
	blogs_all_list = Blog.objects.filter(blog_type=blog_type)	# 筛选出该分类下博客
	context = get_blog_list_common_data(request, blogs_all_list)
	context['blog_type'] = blog_type # 该分类类型
	return render(request, "blog/blogs_with_type.html", context)

# 处理分类博客的页面的方法——按照创建日期分类
def blogs_with_date(request, year, month):
	blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)	# 获取所有博客
	context = get_blog_list_common_data(request, blogs_all_list)
	context['blogs_with_date'] = '%s年%s月' % (year, month)
	return render(request, "blog/blogs_with_date.html", context)

# 具体的blog页面需要传一个参数进来，这个参数就是主键id（主键pk）
def blog_detail(request, blog_pk):
	blog = get_object_or_404(Blog, pk=blog_pk)
	read_cookie_key = read_statistics_once_read(request, blog)
	
	context = {}
	context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last() # 找到比当前博客创建日期大的所有博客集合，last()取最后一条
	context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first() # 找到比当前博客创建日期小的所有博客集合，first()取第一条
	context['blog'] = blog
	# context['login_form'] = LoginForm()

	response = render(request, 'blog/blog_detail.html', context)	# 响应

	# response.set_cookie('blog_%s_read' % blog_pk, 'true')	# set_cookie()方法：跟浏览器说 要把相关数据保存进去。
	# 设置有效期有两种方法：max_age（多长时间内有效，以秒为单位）、expires（指定一个datetime时间）
	# 这两个参数是冲突的，只用设置一个。如果两个参数都不设置的话，则浏览器退出cookie才失效
	response.set_cookie(read_cookie_key, 'true') # 阅读cookie标记
	return response	


