import simplejson
from django.http import HttpResponse
from database.models import Project

#qryProject = Project.objects.values_list('project_name')
#qryProject_json = simplejson.dumps(list(qryProject))

def treeProject(request):
    myTree = {'children': [], 'title': 'Root', 'isFolder': True, 'hideCheckbox': True}
    myTree['children'].append({'title': 'Kingdom', 'isFolder': 'false', 'children': []})
    myTree['children'].append({'title': 'Phylum', 'isFolder': 'false', 'children': []})
    myTree['children'].append({'title': 'Class', 'isFolder': 'false', 'children': []})
    myTree['children'].append({'title': 'Order', 'isFolder': 'false', 'children': []})
    myTree['children'].append({'title': 'Family', 'isFolder': 'false', 'children': []})
    myTree['children'].append({'title': 'Genus', 'isFolder': 'false', 'children': []})
    myTree['children'].append({'title': 'Species', 'isFolder': 'false', 'children': []})

    # Convert result list to a JSON string
    res = simplejson.dumps(myTree, encoding="Latin-1")

    # Support for the JSONP protocol.
    response_dict = {}
    if request.GET.has_key('callback'):
        response_dict = request.GET['callback'] + "(" + res + ")"

    return HttpResponse(response_dict, mimetype='application/json')

    response_dict = {}
    response_dict.update({'children': tree})
    return HttpResponse(response_dict, mimetype='application/javascript')

