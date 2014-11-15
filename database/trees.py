import simplejson
from django.http import StreamingHttpResponse
from models import Project, Sample, Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile


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


def getSelectedSamples(request):
    selected = request.POST.getlist('list')
    with open('uploads/selected.txt', 'wb+') as outfile:
        outfile.write('\n'.join(selected))


def getSampleTree(request):
    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': False,  'checkbox': False, 'expand': True, 'children': []}
    selected = [line.rstrip() for line in open('uploads/selected.txt')]

    q = Sample.objects.values_list('usr_cat1').distinct()
    print q

    #User-categorical
    myNode = {'title': 'usr_cat1', 'isFolder': True, 'children': []}
    for item in sample_names:
        myNode1 = {
            'title': item.usr_cat1,
            'id': item.usr_cat1,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
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


def getTaxaTree(request):
    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': False, 'expand': True, 'children': []}
    selected = [line.rstrip() for line in open("uploads/selected.txt")]
    selected_taxa = Profile.objects.filter(sampleid_id__in=selected).distinct()
    kingdoms = Kingdom.objects.all().filter(kingdomid__in=selected_taxa.values_list('kingdomid')).order_by('kingdomName')
    phylas = Phyla.objects.all().filter(phylaid__in=selected_taxa.values_list('phylaid')).order_by('phylaName')
    classes = Class.objects.all().filter(classid__in=selected_taxa.values_list('classid')).order_by('className')
    orders = Order.objects.all().filter(orderid__in=selected_taxa.values_list('orderid')).order_by('orderName')
    families = Family.objects.all().filter(familyid__in=selected_taxa.values_list('familyid')).order_by('familyName')
    genera = Genus.objects.all().filter(genusid__in=selected_taxa.values_list('genusid')).order_by('genusName')
    species = Species.objects.all().filter(speciesid__in=selected_taxa.values_list('speciesid')).order_by('speciesName')

    for kingdom in kingdoms:
        myNode = {
            'title': kingdom.kingdomName,
            'id': kingdom.kingdomid,
            'tooltip': "Kingdom",
            'isFolder': True,
            'expand': True,
            'children': [],
        }
        for phyla in phylas:
            if phyla.kingdomid_id == kingdom.kingdomid:
                myNode1 = {
                    'title': phyla.phylaName,
                    'id': phyla.kingdomid_id,
                    'tooltip': "Phyla",
                    'isFolder': True,
                    'children': [],
                }
                myNode['children'].append(myNode1)
                for item in classes:
                    if item.phylaid_id == phyla.phylaid:
                        myNode2 = {
                            'title': item.className,
                            'id': item.classid,
                            'tooltip': "Class",
                            'isFolder': True,
                            'children': [],
                        }
                        myNode1['children'].append(myNode2)
                        for order in orders:
                            if order.classid_id == item.classid:
                                myNode3 = {
                                    'title': order.orderName,
                                    'id': order.orderid,
                                    'tooltip': "Order",
                                    'isFolder': True,
                                    'children': [],
                                }
                                myNode2['children'].append(myNode3)
                                for family in families:
                                    if family.orderid_id == order.orderid:
                                        myNode4 = {
                                            'title': family.familyName,
                                            'id': family.familyid,
                                            'tooltip': "Family",
                                            'isFolder': True,
                                            'children': [],
                                        }
                                        myNode3['children'].append(myNode4)
                                        for genus in genera:
                                            if genus.familyid_id == family.familyid:
                                                myNode5 = {
                                                    'title': genus.genusName,
                                                    'id': genus.genusid,
                                                    'tooltip': "Genus",
                                                    'isFolder': True,
                                                    'children': [],
                                                }
                                                myNode4['children'].append(myNode5)
                                                for spec in species:
                                                    if spec.genusid_id == genus.genusid:
                                                        myNode6 = {
                                                            'title': spec.speciesName,
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
