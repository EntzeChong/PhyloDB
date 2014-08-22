import simplejson
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from database.models import Project, Sample
from database.models import Document1
from database.models import Document2
from database.models import Document3
from database.models import Document4
from database.forms import FileUploadForm
from utils import uniqueID, parse_to_list, build_sql, execute_sql

PATH_TO_DB = '../dbMicrobe'
PROJECT = 'database_project'
SAMPLE = 'database_sample'
TAXONOMY = 'database_taxonomy'


def home(request):
    return render_to_response('home.html')


def select(request):
    return render_to_response(
        'select.html',
        context_instance=RequestContext(request)
    )


def getTree(request):
    myTree = {'title': 'All Projects', 'isFolder': 'true', 'children': []}

    projects = Project.objects.all()
    samples = Sample.objects.all()

    for project in projects:
        myNode = {
            'title': 'Project: ' + project.project_name,
            'tooltip': project.project_desc,
            'isFolder': 'true',
            'children': []
        }
        for sample in samples:
            if sample.projectid_id == project.projectid:
                myNode['children'].append({
                    'title': 'Sample: ' + sample.sample_name,
                    'tooltip': sample.title,
                    'isFolder': 'true'
                })
        myTree['children'].append(myNode)

    # Convert result list to a JSON string
    res = simplejson.dumps(myTree, encoding="Latin-1")

    # Support for the JSONP protocol.
    response_dict={}
    if 'callback' in request.GET:
        response_dict = request.GET['callback'] + "(" + res + ")"
    return StreamingHttpResponse(response_dict, content_type='application/json')

    response_dict = {}
    response_dict.update({'children': myTree})
    return StreamingHttpResponse(response_dict, content_type='application/javascript')

def norm(request):
    if request.is_ajax():
        # if request.method == 'POST':
        # selected_samples = request.POST.getlist('id')

        #samples = Sample.objects.all().filter(sampleid__in=selected_samples)
        data = request.POST.body
        print data

    return HttpResponse("OK")


def graph(request):
    organism = Sample.objects.values_list('organism', flat=True).distinct()
    biome = Sample.objects.values_list('biome', flat=True).distinct()
    feature = Sample.objects.values_list('feature', flat=True).distinct()
    geo_loc = Sample.objects.values_list('geo_loc', flat=True).distinct()
    material = Sample.objects.values_list('material', flat=True).distinct()
    crop_rotation = Sample.objects.values_list('crop_rotation', flat=True).distinct()
    cur_land = Sample.objects.values_list('cur_land', flat=True).distinct()
    cur_crop = Sample.objects.values_list('cur_crop', flat=True).distinct()
    cur_cultivar = Sample.objects.values_list('cur_cultivar', flat=True).distinct()
    profile_position = Sample.objects.values_list('profile_position', flat=True).distinct()
    soil_type = Sample.objects.values_list('soil_type', flat=True).distinct()
    tillage = Sample.objects.values_list('tillage', flat=True).distinct()

    return render_to_response(
        'graph.html',
        {'organism': organism,
         'biome': biome,
         'feature': feature,
         'geo_loc': geo_loc,
         'material': material,
         'crop_rotation': crop_rotation,
         'cur_land': cur_land,
         'cur_crop': cur_crop,
         'cur_cultivar': cur_cultivar,
         'profile_position': profile_position,
         'soil_type': soil_type,
         'tillage': tillage
        }
    )


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

    projects = Project.objects.all()

    if request.method == 'POST' and 'Upload' in request.POST:
        parse_files(request)

    if request.method == 'POST' and 'clickMe' in request.POST:
        remove_list(request)

    return render_to_response(
        'upload.html',
        {'projects': projects,
         'form': FileUploadForm},
        context_instance=RequestContext(request)
    )


def parse_files(request):
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

    projects = Project.objects.all()

    return render_to_response(
        'upload.html',
        {'projects': projects},
        context_instance=RequestContext(request)
    )


def remove_list(request):
    items = request.POST.getlist('chkbx')
    for item in items:
        Project.objects.get(projectid=item).delete()

    projects = Project.objects.all()

    return render_to_response(
        'upload.html',
        {'projects': projects},
        context_instance=RequestContext(request)
    )


