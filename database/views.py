import datetime
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import UploadForm1, UploadForm2, UploadForm3, UploadForm4, UploadForm5
from models import Project, Sample, Kingdom, Phyla, Class, Order, Family, Genus, Species
import os
from parsers import parse_project, parse_sample, parse_taxonomy, parse_profile
import pickle
import simplejson
from uuid import uuid4
from utils import handle_uploaded_file, remove_list


def home(request):
    return render_to_response('home.html')


def upload(request):
    if request.method == 'POST' and 'Upload' in request.POST:
        form1 = UploadForm1(request.POST, request.FILES)
        form2 = UploadForm2(request.POST, request.FILES)
        form3 = UploadForm3(request.POST, request.FILES)
        form4 = UploadForm4(request.POST, request.FILES)
        form5 = UploadForm5(request.POST, request.FILES)

        p_uuid = uuid4().hex
        date = datetime.date.today().isoformat()
        dest = "/".join(["uploads", str(p_uuid)])

        if form1.is_valid():
            if form2.is_valid():

                project = ".".join(["project", "csv"])
                file1 = request.FILES['docfile1']
                handle_uploaded_file(file1, dest, project)
                parse_project(dest, date, file1, p_uuid)
                print("Parsed project!")

                sample = ".".join(["sample", "csv"])
                file2 = request.FILES['docfile2']
                handle_uploaded_file(file2, dest, sample)
                parse_sample(file2, p_uuid)
                print("Parsed sample!")

                taxonomy = ".".join(["mothur", "taxonomy"])
                file3 = request.FILES['docfile3']
                handle_uploaded_file(file3, dest, taxonomy)
                parse_taxonomy(file3)
                print("Parsed taxonomy!")

                shared = ".".join(["mothur", "shared"])
                file4 = request.FILES['docfile4']
                handle_uploaded_file(file4, dest, shared)
                parse_profile(dest, p_uuid)
                print("Parsed profile!")

                #taxaprofile(p_uuid)
                #print("Taxa profiles created")

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

    projects = Project.objects.all().order_by('project_name')
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
    projects = Project.objects.all()
    samples = Sample.objects.all()

    return render_to_response(
        'select.html',
        {'projects': projects,
         'samples': samples},
        context_instance=RequestContext(request)
    )


def taxa(request):
    kingdoms = Kingdom.objects.all()
    phylas = Phyla.objects.all()
    classes = Class.objects.all()
    orders = Order.objects.all()
    families = Family.objects.all()
    genera = Genus.objects.all()
    species = Species.objects.all()

    return render_to_response(
        'taxa.html',
        {'kingdoms': kingdoms,
        'phylas': phylas,
        'classes': classes,
        'orders': orders,
        'families': families,
        'genera': genera,
        'species': species},
        context_instance=RequestContext(request)
    )


def alpha_diversity(request):
    return render_to_response(
        'alpha.html',
        context_instance=RequestContext(request)
    )


def beta_diversity(request):
    return render_to_response(
        'beta.html',
        context_instance=RequestContext(request)
    )


def saveCookie(request):
    if request.is_ajax():
        allJson = request.GET["all"]
        selList = simplejson.loads(allJson)
        qs = Sample.objects.all().filter(sampleid__in=selList).values_list('sampleid')
        request.session['selected_samples'] = pickle.dumps(qs.query)

        text = 'Selected sample(s) have been recorded!'
        res = simplejson.dumps(text, encoding="Latin-1")
        return HttpResponse(res, content_type='application/json')


def getCookie(request):
    samples = Sample.objects.all()
    try:
        samples.query = pickle.loads(request.session['selected_samples'])
        return HttpResponse('yes', content_type='application/text')
    except:
        return HttpResponse('no', content_type='application/text')


def instructions(request):
    filename = "samples/Instructions.doc"
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Instructions.doc"'
    response['Content-Length'] = os.path.getsize(filename)
    return response


def project_file(request):
    filename = "samples/Project.csv"
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Project.csv"'
    response['Content-Length'] = os.path.getsize(filename)
    return response


def sample_file(request):
    filename = "samples/Sample.csv"
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Sample.csv"'
    response['Content-Length'] = os.path.getsize(filename)
    return response


def shared_file(request):
    filename = "samples/final.shared"
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="final.shared"'
    response['Content-Length'] = os.path.getsize(filename)
    return response


def taxonomy_file(request):
    filename = "samples/final.taxonomy"
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="final.taxonomy"'
    response['Content-Length'] = os.path.getsize(filename)
    return response