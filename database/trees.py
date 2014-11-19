import simplejson
import pickle
from django.http import StreamingHttpResponse
from models import Project, Sample, Collect, Climate, Soil_class, Soil_nutrient, Management, Microbial, User
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile


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


def getSampleTree(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')

    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': False,  'hideCheckbox': True, 'expand': True, 'children': []}
    mimark = {'title': 'MIMARKs', 'tooltip': 'MIMARKs', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    collect = {'title': 'Sample Collection', 'tooltip': 'Sample Collection', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    climate = {'title': 'Climate', 'tooltip': 'Climate', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_class = {'title': 'Soil Classification', 'tooltip': 'Soil Classification', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_nutrient = {'title': 'Soil Nutrient', 'tooltip': 'Soil Nutrient', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    management = {'title': 'Management', 'tooltip': 'Management', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    microbial = {'title': 'Microbial Biomass', 'tooltip': 'Microbial Biomass', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    user = {'title': 'User-defined', 'tooltip': 'User_defined', 'isFolder': True,  'hideCheckbox': True, 'children': []}

    list = ['sample_name', 'organism', 'seq_method', 'biome', 'feature', 'geo_loc', 'material']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': list[i], 'children': []}
        items = Sample.objects.values_list(str(list[i]), flat='True').filter(sampleid__in=selected).distinct()
        for j in range(len(items)):
            myNode1 = {
                'title': items[j],
                'id': items[j],
                'tooltip': list[i],
                'isFolder': False
            }
            myNode['children'].append(myNode1)
        mimark['children'].append(myNode)

    list = ['collection_date', 'lat_lon', 'elevation']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        mimark['children'].append(myNode)

    list = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': list[i], 'children': []}
        items = Collect.objects.values_list(str(list[i]), flat='True').filter(sampleid_id__in=selected).distinct()
        for j in range(len(items)):
            myNode1 = {
                'title': items[j],
                'id': items[j],
                'tooltip': list[i],
                'isFolder': False
            }
            myNode['children'].append(myNode1)
        collect['children'].append(myNode)

    list = ['samp_size', 'samp_weight_dna_ext']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        collect['children'].append(myNode)

    list = ['annual_season_precpt', 'annual_season_temp']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        climate['children'].append(myNode)

    list = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': list[i], 'children': []}
        items = Soil_class.objects.values_list(str(list[i]), flat='True').filter(sampleid__in=selected).distinct()
        for j in range(len(items)):
            myNode1 = {
                'title': items[j],
                'id': items[j],
                'tooltip': list[i],
                'isFolder': False
            }
            myNode['children'].append(myNode1)
        soil_class['children'].append(myNode)

    list = ['bulk_density', 'porosity', 'slope_gradient', 'water_content_soil']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        soil_class['children'].append(myNode)

    list = ['pH', 'EC', 'tot_C', 'tot_OM', 'tot_N', 'NO3_N', 'NH4_N', 'P', 'K', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'Ca', 'Mg', 'Na', 'B']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        soil_nutrient['children'].append(myNode)

    list = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': list[i], 'children': []}
        items = Management.objects.values_list(str(list[i]), flat='True').filter(sampleid__in=selected).distinct()
        for j in range(len(items)):
            myNode1 = {
                'title': items[j],
                'id': items[j],
                'tooltip': list[i],
                'isFolder': False
            }
            myNode['children'].append(myNode1)
        management['children'].append(myNode)

    list = ['rRNA_copies', 'microbial_biomass_C', 'microbial_biomass_N', 'microbial_respiration']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        microbial['children'].append(myNode)

    list = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': list[i], 'children': []}
        items = User.objects.values_list(str(list[i]), flat='True').filter(sampleid__in=selected).distinct()
        for j in range(len(items)):
            myNode1 = {
                'title': items[j],
                'id': items[j],
                'tooltip': list[i],
                'isFolder': False
            }
            myNode['children'].append(myNode1)
        user['children'].append(myNode)

    list = ['usr_quant1', 'usr_quant2', 'usr_quant3', 'usr_quant4', 'usr_quant5', 'usr_quant6']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        user['children'].append(myNode)

    myTree['children'].append(mimark)
    myTree['children'].append(collect)
    myTree['children'].append(climate)
    myTree['children'].append(soil_class)
    myTree['children'].append(soil_nutrient)
    myTree['children'].append(management)
    myTree['children'].append(microbial)
    myTree['children'].append(user)

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
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    selected_taxa = Profile.objects.filter(sampleid_id__in=selected)

    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': False, 'hideCheckbox': True, 'expand': True, 'children': []}

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
            'children': []
        }
        for phyla in phylas:
            if phyla.kingdomid_id == kingdom.kingdomid:
                myNode1 = {
                    'title': phyla.phylaName,
                    'id': phyla.phylaid,
                    'tooltip': "Phyla",
                    'isFolder': True,
                    'children': []
                }
                myNode['children'].append(myNode1)
                for item in classes:
                    if item.phylaid_id == phyla.phylaid:
                        myNode2 = {
                            'title': item.className,
                            'id': item.classid,
                            'tooltip': "Class",
                            'isFolder': True,
                            'children': []
                        }
                        myNode1['children'].append(myNode2)
                        for order in orders:
                            if order.classid_id == item.classid:
                                myNode3 = {
                                    'title': order.orderName,
                                    'id': order.orderid,
                                    'tooltip': "Order",
                                    'isFolder': True,
                                    'children': []
                                }
                                myNode2['children'].append(myNode3)
                                for family in families:
                                    if family.orderid_id == order.orderid:
                                        myNode4 = {
                                            'title': family.familyName,
                                            'id': family.familyid,
                                            'tooltip': "Family",
                                            'isFolder': True,
                                            'children': []
                                        }
                                        myNode3['children'].append(myNode4)
                                        for genus in genera:
                                            if genus.familyid_id == family.familyid:
                                                myNode5 = {
                                                    'title': genus.genusName,
                                                    'id': genus.genusid,
                                                    'tooltip': "Genus",
                                                    'isFolder': True,
                                                    'children': []
                                                }
                                                myNode4['children'].append(myNode5)
                                                for spec in species:
                                                    if spec.genusid_id == genus.genusid:
                                                        myNode6 = {
                                                            'title': spec.speciesName,
                                                            'id': spec.speciesid,
                                                            'tooltip': "Species",
                                                            'isFolder': False
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


def getGraphData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')

    if request.method == 'GET':
        allJson =request.GET["all"]
        all = simplejson.loads(allJson)
        meta = all["meta"]
        taxa = all["taxa"]

        metaList = meta.split("|")
        metaDict = {}
        c = 0
        while c < metaList.__len__():
            data = metaList[c].split(":")
            key = data[0]
            metaDict.setdefault(key, [])
            value = data[1]
            metaDict[key].append(value)
            c += 1

        taxaList = taxa.split("|")
        taxaDict = {}
        c = 0
        while c < taxaList.__len__():
            data = taxaList[c].split(":")
            key = data[0]
            taxaDict.setdefault(key, [])
            value = data[1]
            taxaDict[key].append(value)
            c += 1

        print metaDict
        print taxaDict

        metaSel = metaDict['sample_name']
        taxaSel = taxaDict['Phyla']

        # Add loop or wildcards here...
        samples = Sample.objects.all().filter(sample_name__in=metaSel).filter(sampleid__in=selected)
        for sample in samples:
            print sample.sample_name

    elif request.method == 'POST':
        formData = dict(request.POST.iterlists())
        nodes = (formData['nodes'])[0].split('|')
        print 'Post: ' + str(nodes)

