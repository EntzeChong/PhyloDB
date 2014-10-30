import simplejson
import datetime
from uuid import uuid4
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Project, Sample, Profile, Kingdom, Phyla, Class, Order, Family, Genus, Species
from forms import UploadForm1, UploadForm2, UploadForm3, UploadForm4, UploadForm5
from trees import getTaxaTree, getSampleTree
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


def graph(request):
   # selected = request.POST.getlist('list')
   # getSampleTree(selected)
   # getTaxaTree(selected)

    return render_to_response(
        'graph.html',
        context_instance=RequestContext(request)
    )


