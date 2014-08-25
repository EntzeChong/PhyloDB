import simplejson
from django.http import StreamingHttpResponse, HttpResponse
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
            'title': project.project_name,
            'tooltip': project.project_desc,
            'isFolder': 'true',
            'children': []
        }
        for sample in samples:
            if sample.projectid_id == project.projectid:
                myNode['children'].append({
                    'title': sample.sample_name,
                    'tooltip': sample.title,
                    'id': sample.sampleid,
                    'isFolder': 'true'
                })
        myTree['children'].append(myNode)

    # Convert result list to a JSON string
    res = simplejson.dumps(myTree, encoding="Latin-1")

    # Support for the JSONP protocol.
    response_dict = {}
    if 'callback' in request.GET:
        response_dict = request.GET['callback'] + "(" + res + ")"
    return StreamingHttpResponse(response_dict, content_type='application/json')

    response_dict = {}
    response_dict.update({'children': myTree})
    return StreamingHttpResponse(response_dict, content_type='application/javascript')


def graph(request):
    items = request.POST.getlist('list')
#    samples = Sample.objects.filter(sampleid__in=items)

    organism = Sample.objects.values_list('organism', flat=True).filter(sampleid__in=items).distinct()
    biome = Sample.objects.values_list('biome', flat=True).filter(sampleid__in=items).distinct()
    feature = Sample.objects.values_list('feature', flat=True).filter(sampleid__in=items).distinct()
    geo_loc = Sample.objects.values_list('geo_loc', flat=True).filter(sampleid__in=items).distinct()
    material = Sample.objects.values_list('material', flat=True).filter(sampleid__in=items).distinct()
    crop_rotation = Sample.objects.values_list('crop_rotation', flat=True).filter(sampleid__in=items).distinct()
    cur_land = Sample.objects.values_list('cur_land', flat=True).filter(sampleid__in=items).distinct()
    cur_crop = Sample.objects.values_list('cur_crop', flat=True).filter(sampleid__in=items).distinct()
    cur_cultivar = Sample.objects.values_list('cur_cultivar', flat=True).filter(sampleid__in=items).distinct()
    profile_position = Sample.objects.values_list('profile_position', flat=True).filter(sampleid__in=items).distinct()
    soil_type = Sample.objects.values_list('soil_type', flat=True).filter(sampleid__in=items).distinct()
    tillage = Sample.objects.values_list('tillage', flat=True).filter(sampleid__in=items).distinct()

 #   t_kingdom = Taxonomy.objects.values_list('t_kingdom', flat=True).distinct()
 #   t_phyla = Taxonomy.objects.values_list('t_phyla', flat=True).distinct()
 #   t_class = Taxonomy.objects.values_list('t_class', flat=True).distinct()
 #   t_order = Taxonomy.objects.values_list('t_order', flat=True).distinct()
 #   t_family = Taxonomy.objects.values_list('t_family', flat=True).distinct()
 #   t_genus = Taxonomy.objects.values_list('t_genus', flat=True).distinct()
 #   t_species = Taxonomy.objects.values_list('t_species', flat=True).distinct()

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


def filter(request):
    items = request.POST.getlist('list')

    samples = Sample.objects.filter(sampleid__in=items)

    projectids = Sample.objects.values_list('projectid_id').filter(sampleid__in=samples)
    projects = Project.objects.filter(projectid__in=projectids)
    print projectids

    return render_to_response(
        'filter.html',
        {'samples': samples,
         'projects': projects},
        context_instance=RequestContext(request)
    )