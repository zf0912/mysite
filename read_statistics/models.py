# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\read_statistics\models.py
from django.db import models
from django.db.models.fields import exceptions
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType # 引用进来ContentType
from django.utils import timezone


class ReadNum(models.Model):
	read_num = models.IntegerField(default=0)
    
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()	# 记录对应模型的组件值。PositiveIntegerField数值类型
	content_object = GenericForeignKey('content_type', 'object_id')	# 把前两行统一起来变成一个通用的外键


class ReadNumExpandMethod():
	def get_read_num(self):
		try:
			ct = ContentType.objects.get_for_model(self)
			readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
			return readnum.read_num
		except exceptions.ObjectDoesNotExist:
			return 0


class ReadDetail(models.Model):	# 记录阅读数量的明细信息(参照上面的ReadNum代码，做简单的改动即可)
	date = models.DateField(default=timezone.now)
	read_num = models.IntegerField(default=0)
    
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()	# 记录对应模型的组件值。PositiveIntegerField数值类型
	content_object = GenericForeignKey('content_type', 'object_id')