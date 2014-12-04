import datetime
import pickle
from uuid import uuid4
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Project, Sample
from forms import UploadForm1, UploadForm2, UploadForm3, UploadForm4, UploadForm5
from utils import handle_uploaded_file, remove_list
from parsers import parse_project, parse_sample, parse_taxonomy, parse_profile, taxaprofile


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
                parse_profile(file3, file4, dest, p_uuid)
                print("Parsed profile!")

                taxaprofile(p_uuid)
                print("Taxa profiles created")

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
    projects = Project.objects.all()
    samples = Sample.objects.all()

    return render_to_response(
        'select.html',
        {'projects': projects,
         'samples': samples},
        context_instance=RequestContext(request)
    )


def graph(request):
    list_unicode = request.POST.getlist('list')
    list_ascii = [s.encode('ascii') for s in list_unicode]

    qs = Sample.objects.all().filter(sampleid__in=list_ascii).values_list('sampleid')
    request.session['selected_samples'] = pickle.dumps(qs.query)

    return render_to_response(
        'graph.html',
        context_instance=RequestContext(request)
    )

