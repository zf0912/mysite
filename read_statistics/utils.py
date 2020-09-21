# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\read_statistics\utils.py
import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail

def read_statistics_once_read(request, obj):
	ct = ContentType.objects.get_for_model(obj)
	key = "%s_%s_read" % (ct.model, obj.pk)	# 模型名称，主键值
	# 对应views.py中判断cookie是否存在：if not request.COOKIES.get('blog_%s_read' % blog_pk)，和设置cookie的方法： response.set_cookie('blog_%s_read' % blog_pk, 'true')

	if not request.COOKIES.get(key):
		# 总阅读数 +1
		# 返回结果：第一个是我们所需要对象，第二个表示是否创建（如果是创建的，为true；如果是获取到的，为false
		readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk) 
		readnum.read_num +=1
		readnum.save()

		# 当天阅读数 +1
		date = timezone.now().date()
		readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
		readDetail.read_num += 1
		readDetail.save()
	return key

	'''
	if not request.COOKIES.get(key): # 当不存在这个键值的时候，我们才进行阅读加1的操作
		# ct = ContentType.objects.get_for_model(Blog)
		if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
			# 存在记录
			readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
		else:
			# 不存在对应的记录
			readnum = ReadNum(content_type=ct, object_id=obj.pk)
		# 计数加1
		readnum.read_num +=1
		readnum.save()

		date = timezone.now().date()
		if ReadDetail.objects.filter(content_type=ct, object_id=obj.pk, date=date).count():
			readDetail = ReadDetail.objects.get(content_type=ct, object_id=obj.pk, date=date)
		else:
			readDetail = ReadDetail(content_type=ct, object_id=obj.pk, date=date)
		readDetail.read_num += 1
		readDetail.save()
	'''

def get_seven_days_read_data(content_type):	# 我们要做成一个通用的统计方法，所以这里传入content_type类型这个参数
	today = timezone.now().date() # 获取当天日期
	dates = []
	read_nums = []
	# for i in range(7, 0, -1):
	for i in range(6, -1, -1):
		date = today - datetime.timedelta(days=i)	# timedelta:差值
		dates.append(date.strftime('%m/%d'))	# date.strftime()：把日期变成字符串
		read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
		result = read_details.aggregate(read_num_sum=Sum('read_num')) # 对read_num字段进行求和，取名为read_num_sum
		read_nums.append(result['read_num_sum'] or 0)
	return dates, read_nums

# 今天的数据统计
# 传入一个博客类型进来，筛选出日期和博客类型，然后根据阅读数量进行倒序排序
def get_today_hot_data(content_type):
	today = timezone.now().date()
	read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
	return read_details[:7]
	 
# 昨天的数据统计
def get_yesterday_hot_data(content_type):
	today = timezone.now().date()
	yesterday = today - datetime.timedelta(days=1)
	read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
	return read_details[:7]

'''
# 7天的数据统计
def get_7_days_hot_data(content_type):
	today = timezone.now().date()
	date = today - datetime.timedelta(days=7)
	# date_lt=today,date__gte=date：小于今天，大于等于前7天。然后按照博客id分组统计阅读量，即分组+求和
	# 这个values方法是将查询集变成一个迭代器，迭代器里元素是字典，后面指定参数就可以取出每项的键值对，之后进行求和，类似于sql中的group后再sum
	# values对应实现分组，然后annotate实现求和
	read_details = ReadDetail.objects \
							 .filter(content_type=content_type, date_lt=today,date__gte=date) \
							 .values('content_type', 'object_id') \
							 .annotate(read_num_sum = Sum('read_num')) \
							 .order_by('-read_num')
	return read_details[:7]
'''