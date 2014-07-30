from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader, Context
from database.models import Project

# Create your views here.
def home(request):
    return render_to_response('home.html')

def upload(request):
    return render_to_response('upload.html')

def select(request):
    return render_to_response('select.html')

def norm(request):
    return render_to_response('norm.html')
