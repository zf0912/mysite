# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\blog\models.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from read_statistics.models import ReadNumExpandMethod, ReadDetail


# 博客类型
class BlogType(models.Model):
	type_name = models.CharField(max_length=15)

	def __str__(self):
		return self.type_name

	class Meta:	
		verbose_name = "博客类型" # 单数时显示
		verbose_name_plural = verbose_name # 复数时显示

# 博客
class Blog(models.Model, ReadNumExpandMethod):
	title = models.CharField(max_length=50, verbose_name="标题")
	blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE, verbose_name="博客类型")	# 外键关联
	# content = models.TextField()
	# content = RichTextField()
	content = RichTextUploadingField()
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	read_details = GenericRelation(ReadDetail)
	# read_num = models.IntegerField(default=0)
	created_time = models.DateTimeField(auto_now_add=True)
	last_updated_time = models.DateTimeField(auto_now=True)

	def get_url(self):
		return reverse('blog_detail', kwargs={'blog_pk': self.pk})
		
	def get_user(self):
		return self.author

	def get_email(self):
		return self.author.email
	
	def __str__(self):
		return "<Blog:%s>" % self.title

	class Meta:	
		# 设置排序信息，一个列表：第一排序、第二排序（这里只用到一个排序）。
		ordering = ['-created_time'] # 按照创建时间倒序排序
		verbose_name = "博客" # 单数时显示
		verbose_name_plural = "博客" # 复数时显示
