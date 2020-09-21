# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\mysite\admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline): # 创建一个inline行内链接
    model = Profile # 指向的模型是Profile
    can_delete = False # 不允许删除


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )	# 继承了BaseUserAdmin的基础上，加多一个ProfileInline
    list_display = ('username', 'nickname', 'email', 'is_staff', 'is_active', 'is_superuser') 
    # 除了nickname字段，其他字段都是继承的BaseUserAdmin(即UserAdmin)里面带有的字段
    
    # 但是是没有nicknam这个字段的，这个字段是Profile的，因为是一对一关联，，所以这个一个user会对应一个profile。我们可以通过user直接找到Profile这个模型。
    # 这里没有nickname，我们可以自定义这个字段
    def nickname(self, obj):
    	return obj.profile.nickname
    nickname.short_description = '昵称' # 显示成中文

admin.site.unregister(User) # 先取消注册
admin.site.register(User, UserAdmin)	# 然后重新注册User到Admin里面


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'nickname')
