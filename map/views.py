from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def home_view(*args, **kwargs):
	# simple hello world view
	# all views will be linked to an actual HTML file when the project gets bigger
	return HttpResponse("<h1>Hello District MAKKERs</h1>")