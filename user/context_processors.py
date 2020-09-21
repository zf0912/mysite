# # C:\Users\12482\Desktop\py_learn\Django2.0_chapter46\mysite_env\mysite\user\context_processors.py
from .forms import LoginForm


def login_modal_form(request):
	return {'login_modal_form': LoginForm()}