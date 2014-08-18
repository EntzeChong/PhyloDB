import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from database.models import Project, Sample, Taxonomy
from database.utils import replace_all


def treeProject(request):
    myTree = {'title': 'root', 'isFolder': True, 'hideCheckbox': True, 'expand': True, 'child1': []}

    # iterate over database and add project/samples
    for project_name in Project.objects.values_list('project_name'):
            myTree['child1'].append(
                {'title': project_name, 'isFolder': True, 'hideCheckbox': False, 'expand': False, 'child2': []})
#           proj = Project.objects.value_list('projectid').filter(project_name=project_name)
#           for sample_name in Sample.objects.values_list('sample_name'):
#               myTree['child2'].append(
#                   {'title': sample_name, 'isFolder': False, 'hideCheckbox': False, 'expand': False})

    # Convert dictionary to a JSON string
    data = json.dumps(myTree)

    # replace
    rep = {'child1': 'children', 'child2': 'children', 'child3': 'children'}
    res = replace_all(data, rep)

    # Support for the JSONP protocol.
    response_dict = {}
    if request.GET.has_key('callback'):
        response_dict = request.GET['callback'] + "(" + res + ")"

    return HttpResponse(response_dict, content_type='application/json')
