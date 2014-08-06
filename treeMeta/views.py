from django.http import HttpResponse
import simplejson


def treeMeta(request):
    myTree = {'children': [], 'title': 'MetaData', 'isFolder': True, 'hideCheckbox': True}
    myTree['children'].append({'title': 'Variable 1', 'isFolder': 'false', 'children': []})
    myTree['children'].append({'title': 'Variable 2', 'isFolder': 'false', 'children': []})
    myTree['children'].append({'title': 'Variable 3', 'isFolder': 'false', 'children': []})

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