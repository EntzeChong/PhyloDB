from django.shortcuts import render_to_response


def home(request):
    return render_to_response('home.html')

def upload(request):
    return render_to_response('upload.html')

def select(request):
    return render_to_response('select.html')

def norm(request):
    return render_to_response('norm.html')

def graph(request):
    return render_to_response('graph.html')