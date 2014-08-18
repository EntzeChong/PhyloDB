from django.shortcuts import render_to_response
from django.template import RequestContext
from database.models import Project, Sample, Taxonomy
from database.models import Document1
from database.models import Document2
from database.models import Document3
from database.models import Document4
from database.forms import FileUploadForm
from utils import uniqueID, parse_to_list, build_sql, execute_sql
import os

PATH_TO_DB = '../dbMicrobe'
PROJECT = 'database_project'
SAMPLE = 'database_sample'
TAXONOMY = 'database_taxonomy'


def home(request):
    return render_to_response('home.html')


def select(request):
    projects = Project.objects.all()
    samples = Sample.objects.all()

    return render_to_response(
        'select.html',
        {'projects': projects,
         'samples': samples}
    )


def norm(request):
    return render_to_response('norm.html')


def graph(request):
    return render_to_response('graph.html')


def upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc1 = Document1(docfile1=request.FILES['docfile1'])
            newdoc1.save()
            newdoc2 = Document2(docfile2=request.FILES['docfile2'])
            newdoc2.save()
            newdoc3 = Document3(docfile3=request.FILES['docfile3'])
            newdoc3.save()
            newdoc4 = Document4(docfile4=request.FILES['docfile4'])
            newdoc4.save()

            # update Project/Sample tables in dbMicrobe
            f_project = open('uploads/temp/meta_Project.csv', 'r')
            f_in_project = parse_to_list(f_project, ',')
            f_sample = open('uploads/temp/meta_Sample.csv', 'r')
            f_in_sample = parse_to_list(f_sample, ',')
            for record_project in f_in_project:
                p_uuid = uniqueID()
                record_project.insert(0, p_uuid)
                sql_project = build_sql(PROJECT, record_project)
                execute_sql(sql_project)
                for record_sample in f_in_sample:
                    s_uuid = uniqueID()
                    record_sample.insert(0, s_uuid)
                    record_sample.insert(1, p_uuid)
                    sql_sample = build_sql(SAMPLE, record_sample)
                    execute_sql(sql_sample)

            # update Taxonomy table in dbMicrobe
#            f_cons = open('uploads/temp/*.taxonomy')
#            f_in = parse_to_list(f_cons, '\t')

    projects = Project.objects.all()

    return render_to_response(
        'upload.html',
        {'projects': projects,
        'form': FileUploadForm},
        context_instance=RequestContext(request)
    )





