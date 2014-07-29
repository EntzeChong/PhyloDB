from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader, Context
from database.models import Project

# Create your views here.
def home(request):
    return render_to_response('home.html')


'''def home(request):
    project_list = Project.objects.all()
    t = loader.get_template('home.html')
    c = Context({
        'project_list': project_list,
    })
    return HttpResponse(t.render(c))
'''