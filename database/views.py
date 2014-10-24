import simplejson
import datetime
from uuid import uuid4
from django.http import StreamingHttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Project, Sample, Taxonomy
from forms import UploadForm1, UploadForm2, UploadForm3, UploadForm4, UploadForm5
from utils import handle_uploaded_file, remove_list
from parsers import parse_project, parse_sample


def home(request):
    return render_to_response('home.html')


def upload(request):
    if request.method == 'POST' and 'Upload' in request.POST:
        form1 = UploadForm1(request.POST, request.FILES)
        form2 = UploadForm2(request.POST, request.FILES)
        form3 = UploadForm3(request.POST, request.FILES)
        form4 = UploadForm4(request.POST, request.FILES)
        form5 = UploadForm5(request.POST, request.FILES)

        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        p_uuid = uuid4().hex
        date = "-".join([str(year), str(month), str(day)])
        dest = "/".join(["uploads", str(p_uuid)])

        if form1.is_valid():
            if form2.is_valid():
                name = ".".join(["project", "csv"])
                file = request.FILES['docfile1']
                handle_uploaded_file(file, dest, name)
                parse_project(dest, name, date, p_uuid)

                name = ".".join(["sample", "csv"])
                file = request.FILES['docfile2']
                handle_uploaded_file(file, dest, name)
                parse_sample(dest, name, p_uuid)

                name = ".".join(["mothur", "taxonomy"])
                file = request.FILES['docfile3']
                handle_uploaded_file(file, dest, name)
                #parse_taxonomy(dest, name, p_uuid)

                name = ".".join(["mothur", "shared"])
                file = request.FILES['docfile4']
                handle_uploaded_file(file, dest, name)
                #parse_shared(dest, name, p_uuid)

            # if biom file has metadata then we don't need form1
            elif form3.is_valid():
                name = ".".join(["project", "csv"])
                file = request.FILES['docfile1']
                handle_uploaded_file(file, dest, name)

                name = ".".join(["sample", "csv"])
                file = request.FILES['docfile2']
                handle_uploaded_file(file, dest, name)

                name = ".".join(["biom_1.5", "txt"])
                file = request.FILES['docfile5']
                handle_uploaded_file(file, dest, name)

            elif form4.is_valid():
                name = ".".join(["project", "csv"])
                file = request.FILES['docfile1']
                handle_uploaded_file(file, dest, name)

                name = ".".join(["sample", "csv"])
                file = request.FILES['docfile2']
                handle_uploaded_file(file, dest, name)

                name = ".".join(["biom_1.4", "txt"])
                file = request.FILES['docfile6']
                handle_uploaded_file(file, dest, name)

            elif form5.is_valid():
                name = ".".join(["project", "csv"])
                file = request.FILES['docfile1']
                handle_uploaded_file(file, dest, name)

                name = ".".join(["sample", "csv"])
                file = request.FILES['docfile2']
                handle_uploaded_file(file, dest, name)

                name = ".".join(["biom_1.4", "txt"])
                file = request.FILES['docfile7']
                handle_uploaded_file(file, dest, name)

            else:
                print("Please upload taxonomic profile data")

        else:
            print("Please upload meta files")

    elif request.method == 'POST' and 'clickMe' in request.POST:

        remove_list(request)

    projects = Project.objects.all()

    return render_to_response(
        'upload.html',
        {'projects': projects,
         'form1': UploadForm1,
         'form2': UploadForm2,
         'form3': UploadForm3,
         'form4': UploadForm4,
         'form5': UploadForm5},
        context_instance=RequestContext(request)
    )


def select(request):
    return render_to_response(
        'select.html',
        context_instance=RequestContext(request)
    )


def getTree(request):
    myTree = {'title': 'All Projects', 'isFolder': True, 'expand': True, 'children': []}

    projects = Project.objects.all()
    samples = Sample.objects.all()

    for project in projects:
        myNode = {
            'title': project.project_name,
            'tooltip': project.project_desc,
            'isFolder': True,
            'children': []
        }
        for sample in samples:
            if sample.projectid_id == project.projectid:
                myNode['children'].append({
                    'title': sample.sample_name,
                    'tooltip': sample.title,
                    'id': sample.sampleid,
                    'isFolder': False
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


def filter(request):
    items = request.POST.getlist('list')

    samples = Sample.objects.filter(sampleid__in=items)

    projectids = Sample.objects.values_list('projectid_id').filter(sampleid__in=samples)
    projects = Project.objects.filter(projectid__in=projectids)

    taxa = Taxonomy.objects.all()
    print taxa

    return render_to_response(
        'filter.html',
        {'samples': samples,
         'projects': projects},
        context_instance=RequestContext(request)
    )


#def norm(request):
    #get post from filter page and do stuff...


