from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from database.models import Document1
from database.models import Document2
from database.models import Document3
from database.models import Document4
from database.forms import DocumentForm


def home(request):
    return render_to_response('home.html')


def select(request):
    return render_to_response('select.html')


def norm(request):
    return render_to_response('norm.html')


def graph(request):
    return render_to_response('graph.html')


def upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc1 = (Document1(docfile1 = request.FILES['docfile1']))
            newdoc1.save()
            newdoc2 = (Document2(docfile2 = request.FILES['docfile2']))
            newdoc2.save()
            newdoc3 = (Document3(docfile3 = request.FILES['docfile3']))
            newdoc3.save()
            newdoc4 = (Document4(docfile4 = request.FILES['docfile4']))
            newdoc4.save()
    else:
        form = DocumentForm() # A empty, unbound form

    return render_to_response(
        'upload.html', {'form': form},
        context_instance=RequestContext(request)
    )
