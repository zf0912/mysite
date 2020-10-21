# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\comment\views.py
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import JsonResponse
# from django.utils.html import strip_tags
# from notifications.signals import notify
# from django.core.mail import send_mail
# from django.conf import settings
from .models import Comment
from .forms import CommentForm

def update_comment(request):
	referer = request.META.get('HTTP_REFERER', reverse('home'))
	comment_form = CommentForm(request.POST, user=request.user)	# 实例化
	data ={}

	# 验证。如果有效，则保存数据
	if comment_form.is_valid():	
		# 检查通过，保存数据
		comment = Comment()	# 模型实例化
		comment.user = comment_form.cleaned_data['user']
		comment.text = comment_form.cleaned_data['text']
		comment.content_object = comment_form.cleaned_data['content_object'] # 在forms.py中将model_obj写入到cleaned_data，这里从cleaned_data中获取到
		
		# 判断数据是不是回复
		parent = comment_form.cleaned_data['parent']
		if not parent is None:
			comment.root = parent.root if not parent.root is None else parent # 判断上一级是否为顶级评论：如果是，就填入parent，如果不是，就写入parent.root???
			comment.parent = parent
			comment.reply_to = parent.user
		comment.save()

		'''
		# 发送站内消息
		if comment.reply_to is None: # 如果reply_to是None的话，那么就是评论，否则就是评论
			# 评论
			# 如果是评论的话，需要找到评论的主体（我们这里是博客）
			recipient = comment.content_object.get_user()
			if comment.content_type.model == 'blog':
				blog = comment.content_object
				verb = '{0} 评论了你的 《{1}》'.format(comment.user.get_nickname_or_username(), blog.title)
			else:
				raise Exception('unknow comment object type')
		else:
			# 回复
			recipient = comment.reply_to
			verb = '{0} 回复了你的评论“{1}”'.format(
					comment.user.get_nickname_or_username(), 
					strip_tags(comment.parent.text)
				)

		notify.send(comment.user, recipient=recipient, verb=verb, action_object=comment) # 参数：发送者、接收者（可以是一个也可以是多个，可能是评论一篇博客，也可能是回复评论，所以需要做一个判断是评论还是回复）、内容、触发的位置
		'''

		# 发送邮件通知
		# comment.send_mail()
		
		'''
		if comment.parent is None:
			# 评论博客的
			subject = '有人评论你的博客'
			email = comment.content_object.get_email()
		else:
			# 回复评论的
			subject = '有人回复你的评论'
			email = comment.reply_to.email		
		# 5个参数为：主题、邮件内容、发送的邮箱（settings中已经设置好了）、要发送到哪个邮箱、发送错误是否抛出错误
		if email != '':
			text = comment.text + '\n' + comment.content_object.get_url()	# 反向解析得到链接
			send_mail(subject, text, settings.EMAIL_HOST_USER, [email], fail_silently=False)
		'''


		# 返回数据
		data['status'] = 'SUCCESS'
		# data['username'] = comment.user.username
		data['username'] = comment.user.get_nickname_or_username()
		# data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
		data['comment_time'] = comment.comment_time.timestamp()
		data['text'] = comment.text
		data['content_type'] = ContentType.objects.get_for_model(comment).model # model属性得到ContentType对应的字符串
		if not parent is None:
			# data['reply_to'] = comment.reply_to.username
			data['reply_to'] = comment.reply_to.get_nickname_or_username()
		else:
			data['reply_to'] = ''
		data['pk'] = comment.pk
		data['root_pk'] = comment.root.pk if not comment.root is None else ''


	# 如果验证错误，则返回错误信息
	else:		
		# 返回数据
		data['status'] = 'ERROR'
		data['message'] = list(comment_form.errors.values())[0][0]
		# return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer })		
	return JsonResponse(data)

'''
def update_comment(request):
	referer = request.META.get('HTTP_REFERER', reverse('home'))
	# 数据检查
	# user = request.user
	if not request.user.is_authenticated:
		return render(request, 'error.html', {'message': '用户未登录', 'redirect_to': referer })

	text = request.POST.get('text', '').strip() # .srtip()去掉前后多余的空格
	# 一般这里需要在提交之前 在前端页面对它进行判断，但是有个原则：前端页面不可信。
	# 不管前端页面判断做得多么准确，但是总会有一些方法绕开这些判断
	if text == '':	
		return render(request, 'error.html', {'message': '评论内容为空', 'redirect_to': referer })
	try:
		content_type = request.POST.get('content_type', '')
		object_id = int(request.POST.get('object_id', ''))
		# ContentType.objects.get(model=content_type)得到具体博客的ContentType类型，再.model_class()由类型得到Blog具体模型这个class
		model_class = ContentType.objects.get(model=content_type).model_class()
		model_obj = model_class.objects.get(pk=object_id)
	except Exception as e:
		return render(request, 'error.html', {'message': '评论对象不存在', 'redirect_to': referer })

	# 检查通过，保存数据
	comment = Comment()	# 模型实例化
	comment.user = request.user
	comment.text = text
	# Blog.objects.get(pk=object_id)
	comment.content_object = model_obj # content_object是一个具体的博客对象，我们要通过content_type和object_id这两个去得到。
	# 而我们通常获取博客是通过Blog这个模型 Blog.objects.get(pk=object_id)来获取得到的，这里没有Blog模型，可以直接引用。
	# 还有另外一种途径，我们可以根据ContentType这个类型进行处理（这里建议用这种方法处理）
	comment.save()

	# referer = request.META.get('HTTP_REFERER', reverse('home'))
	return redirect(referer) # 处理完毕，还需要返回一个内容给前端页面，跟登陆一样的操作，重定向回到原来的页面
'''


