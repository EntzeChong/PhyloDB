import os
import shutil
from models import Project, Document1, Document2, Document3, Document4, Document5, Document6, Document7


def handle_uploaded_file(f, path, name):
    if not os.path.exists(path):
        os.makedirs(path)
    dest = "/".join([str(path), str(name)])
    with open(str(dest), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def remove_list(request):
    items = request.POST.getlist('chkbx')
    for item in items:
        Project.objects.get(projectid=item).delete()

        if Document1.objects.filter(projectid=item).exists():
            query = Document1.objects.get(projectid=item)
            path = query.path
            if os.path.exists(path):
                shutil.rmtree(str(path))
            Document1.objects.get(projectid=item).delete()

        if Document2.objects.filter(projectid=item).exists():
            query = Document2.objects.get(projectid=item)
            path = query.path
            if os.path.exists(path):
                shutil.rmtree(str(path))
            Document2.objects.get(projectid=item).delete()

        if Document3.objects.filter(projectid=item).exists():
            query = Document3.objects.get(projectid=item)
            path = query.path
            if os.path.exists(path):
                shutil.rmtree(str(path))
            Document3.objects.get(projectid=item).delete()

        if Document4.objects.filter(projectid=item).exists():
            query = Document4.objects.get(projectid=item)
            path = query.path
            if os.path.exists(path):
                shutil.rmtree(str(path))
            Document4.objects.get(projectid=item).delete()

        if Document5.objects.filter(projectid=item).exists():
            query = Document5.objects.get(projectid=item)
            path = query.path
            if os.path.exists(path):
                shutil.rmtree(str(path))
            Document5.objects.get(projectid=item).delete()

        if Document6.objects.filter(projectid=item).exists():
            query = Document6.objects.get(projectid=item)
            path = query.path
            if os.path.exists(path):
                shutil.rmtree(str(path))
            Document6.objects.get(projectid=item).delete()

        if Document7.objects.filter(projectid=item).exists():
            query = Document7.objects.get(projectid=item)
            path = query.path
            if os.path.exists(path):
                shutil.rmtree(str(path))
            Document7.objects.get(projectid=item).delete()





