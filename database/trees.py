import simplejson
from django.http import StreamingHttpResponse
from models import Project, Sample, Profile, Kingdom, Phyla, Class, Order, Family, Genus, Species


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
        outfile.write("\n".join(selected))


def getSampleTree(request):
    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': True, 'expand': True, 'children': []}

    selected = open("uploads/selected.txt").readlines()
    samples = Sample.objects.all().filter(sampleid__in=selected).distinct()

    myNode = {'title': 'Organism', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.organism,
            'id': sample.organism,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'Biome', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.biome,
            'id': sample.biome,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'feature', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.feature,
            'id': sample.feature,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'geo_loc', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.geo_loc,
            'id': sample.geo_loc,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'material', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.material,
            'id': sample.material,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'crop_rotation', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.crop_rotation,
            'id': sample.crop_rotation,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'cur_land', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.cur_land,
            'id': sample.cur_land,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'cur_crop', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.cur_crop,
            'id': sample.cur_crop,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'cur_cultivar', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.cur_cultivar,
            'id': sample.cur_cultivar,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'soil_type', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.soil_type,
            'id': sample.soil_type,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'tillage', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.tillage,
            'id': sample.tillage,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'user_1', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.user_1,
            'id': sample.user_1,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'user_2', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.user_2,
            'id': sample.user_2 ,
            'isFolder': False,
        }
        myNode['children'].append(myNode1)
    myTree['children'].append(myNode)

    myNode = {'title': 'user_3', 'isFolder': True, 'children': []}
    for sample in samples:
        myNode1 = {
            'title': sample.user_3,
            'id': sample.user_3,
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
    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': True, 'expand': True, 'children': []}

    selected = open("uploads/selected.txt").readlines()
    selected_taxa = Profile.objects.filter(sampleid__in=selected).distinct()

    kingdoms = Kingdom.objects.all().filter(kingdomid__in=selected_taxa.values_list('kingdomid')).order_by('t_kingdom')
    phylas = Phyla.objects.all().filter(phylaid__in=selected_taxa.values_list('phylaid')).order_by('t_phyla')
    classes = Class.objects.all().filter(classid__in=selected_taxa.values_list('classid')).order_by('t_class')
    orders = Order.objects.all().filter(orderid__in=selected_taxa.values_list('orderid')).order_by('t_order')
    families = Family.objects.all().filter(familyid__in=selected_taxa.values_list('familyid')).order_by('t_family')
    genera = Genus.objects.all().filter(genusid__in=selected_taxa.values_list('genusid')).order_by('t_genus')
    species = Species.objects.all().filter(speciesid__in=selected_taxa.values_list('speciesid')).order_by('t_species')

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
                    'id': phyla.kingdomid_id,
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
