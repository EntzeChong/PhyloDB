import simplejson
import datetime
from uuid import uuid4
from django.http import StreamingHttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Project, Sample, Profile, Kingdom, Phyla, Class, Order, Family, Genus, Species
from forms import UploadForm1, UploadForm2, UploadForm3, UploadForm4, UploadForm5
from utils import handle_uploaded_file, remove_list
from parsers import parse_project, parse_sample, parse_taxonomy, parse_profile


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
                project = ".".join(["project", "csv"])
                file = request.FILES['docfile1']
                handle_uploaded_file(file, dest, project)
                parse_project(dest, project, date, p_uuid)

                sample = ".".join(["sample", "csv"])
                file = request.FILES['docfile2']
                handle_uploaded_file(file, dest, sample)
                parse_sample(dest, sample, p_uuid)

                taxonomy = ".".join(["mothur", "taxonomy"])
                file = request.FILES['docfile3']
                handle_uploaded_file(file, dest, taxonomy)
                parse_taxonomy(dest, taxonomy)

                shared = ".".join(["mothur", "shared"])
                file = request.FILES['docfile4']
                handle_uploaded_file(file, dest, shared)
                parse_profile(dest, taxonomy, shared, p_uuid)

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


def getProjectTree(request):
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
    selected_samples = request.POST.getlist('list')

    counts = Profile.objects.all()

    organism = Sample.objects.values_list('organism', flat=True).filter(sampleid__in=selected_samples).distinct()
    biome = Sample.objects.values_list('biome', flat=True).filter(sampleid__in=selected_samples).distinct()
    feature = Sample.objects.values_list('feature', flat=True).filter(sampleid__in=selected_samples).distinct()
    geo_loc = Sample.objects.values_list('geo_loc', flat=True).filter(sampleid__in=selected_samples).distinct()
    material = Sample.objects.values_list('material', flat=True).filter(sampleid__in=selected_samples).distinct()
    crop_rotation = Sample.objects.values_list('crop_rotation', flat=True).filter(sampleid__in=selected_samples).distinct()
    cur_land = Sample.objects.values_list('cur_land', flat=True).filter(sampleid__in=selected_samples).distinct()
    cur_crop = Sample.objects.values_list('cur_crop', flat=True).filter(sampleid__in=selected_samples).distinct()
    cur_cultivar = Sample.objects.values_list('cur_cultivar', flat=True).filter(sampleid__in=selected_samples).distinct()
    profile_position = Sample.objects.values_list('profile_position', flat=True).filter(sampleid__in=selected_samples).distinct()
    soil_type = Sample.objects.values_list('soil_type', flat=True).filter(sampleid__in=selected_samples).distinct()
    tillage = Sample.objects.values_list('tillage', flat=True).filter(sampleid__in=selected_samples).distinct()

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
         'tillage': tillage,
         'counts': counts,
        }
    )


def getTaxaTree(request):
    kingdoms = Kingdom.objects.all().order_by('t_kingdom')
    phylas = Phyla.objects.all().order_by('t_phyla')
    classes = Class.objects.all().order_by('t_class')
    orders = Order.objects.all().order_by('t_order')
    families = Family.objects.all().order_by('t_family')
    genera = Genus.objects.all().order_by('t_genus')
    species = Species.objects.all().order_by('t_species')

    myTree = {'title': 'Root', 'tooltip': "Root", 'isFolder': True, 'expand': True, 'children': []}

    for kingdom in kingdoms:
        myNode = {
            'title': kingdom.t_kingdom,
            'id': kingdom.kingdomid,
            'tooltip': "Kingdom",
            'isFolder': True,
            'expand': True,
            'children': [],
        }
        for phyla in phylas:
            if phyla.kingdomid_id == kingdom.kingdomid:
                myNode1 = {
                    'title': phyla.t_phyla,
                    'id': phyla.phylaid,
                    'tooltip': "Phyla",
                    'isFolder': True,
                    'children': [],
                }
                myNode['children'].append(myNode1)
                for item in classes:
                    if item.phylaid_id == phyla.phylaid:
                        myNode2 = {
                            'title': item.t_class,
                            'id': item.classid,
                            'tooltip': "Class",
                            'isFolder': True,
                            'children': [],
                        }
                        myNode1['children'].append(myNode2)
                        for order in orders:
                            if order.classid_id == item.classid:
                                myNode3 = {
                                    'title': order.t_order,
                                    'id': order.orderid,
                                    'tooltip': "Order",
                                    'isFolder': True,
                                    'children': [],
                                }
                                myNode2['children'].append(myNode3)
                                for family in families:
                                    if family.orderid_id == order.orderid:
                                        myNode4 = {
                                            'title': family.t_family,
                                            'id': family.familyid,
                                            'tooltip': "Family",
                                            'isFolder': True,
                                            'children': [],
                                        }
                                        myNode3['children'].append(myNode4)
                                        for genus in genera:
                                            if genus.familyid_id == family.familyid:
                                                myNode5 = {
                                                    'title': genus.t_genus,
                                                    'id': genus.genusid,
                                                    'tooltip': "Genus",
                                                    'isFolder': True,
                                                    'children': [],
                                                }
                                                myNode4['children'].append(myNode5)
                                                for spec in species:
                                                    if spec.genusid_id == genus.genusid:
                                                        myNode6 = {
                                                            'title': spec.t_species,
                                                            'id': spec.speciesid,
                                                            'tooltip': "Species",
                                                            'isFolder': False,
                                                        }
                                                        myNode5['children'].append(myNode6)
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
