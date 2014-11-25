import simplejson
import pickle
import operator
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q, Avg, Count, StdDev
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


def getSampleCatTree(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')

    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': False,  'hideCheckbox': True, 'expand': True, 'children': []}
    mimark = {'title': 'MIMARKs', 'tooltip': 'MIMARKs', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    collect = {'title': 'Sample Collection', 'tooltip': 'Sample Collection', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_class = {'title': 'Soil Classification', 'tooltip': 'Soil Classification', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    management = {'title': 'Management', 'tooltip': 'Management', 'isFolder': True,  'hideCheckbox': True, 'children': []}
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

    myTree['children'].append(mimark)
    myTree['children'].append(collect)
    myTree['children'].append(soil_class)
    myTree['children'].append(management)
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


def getSampleQuantTree(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')

    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': False,  'hideCheckbox': True, 'expand': True, 'children': []}
    mimark = {'title': 'MIMARKs', 'tooltip': 'MIMARKs', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    collect = {'title': 'Sample Collection', 'tooltip': 'Sample Collection', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    climate = {'title': 'Climate', 'tooltip': 'Climate', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_class = {'title': 'Soil Classification', 'tooltip': 'Soil Classification', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_nutrient = {'title': 'Soil Nutrient', 'tooltip': 'Soil Nutrient', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    microbial = {'title': 'Microbial Biomass', 'tooltip': 'Microbial Biomass', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    user = {'title': 'User-defined', 'tooltip': 'User_defined', 'isFolder': True,  'hideCheckbox': True, 'children': []}

    list = ['collection_date', 'lat_lon', 'elevation']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        mimark['children'].append(myNode)

    list = ['samp_size', 'samp_weight_dna_ext']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        collect['children'].append(myNode)

    list = ['annual_season_precpt', 'annual_season_temp']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        climate['children'].append(myNode)

    list = ['bulk_density', 'porosity', 'slope_gradient', 'water_content_soil']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        soil_class['children'].append(myNode)

    list = ['pH', 'EC', 'tot_C', 'tot_OM', 'tot_N', 'NO3_N', 'NH4_N', 'P', 'K', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'Ca', 'Mg', 'Na', 'B']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        soil_nutrient['children'].append(myNode)

    list = ['rRNA_copies', 'microbial_biomass_C', 'microbial_biomass_N', 'microbial_respiration']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        microbial['children'].append(myNode)

    list = ['usr_quant1', 'usr_quant2', 'usr_quant3', 'usr_quant4', 'usr_quant5', 'usr_quant6']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': list[i], 'isFolder': False}
        user['children'].append(myNode)

    myTree['children'].append(mimark)
    myTree['children'].append(collect)
    myTree['children'].append(climate)
    myTree['children'].append(soil_class)
    myTree['children'].append(soil_nutrient)
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


def getCatGraphData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        metaDict = {}
        if all["meta"]:
            meta = all["meta"]
            metaList = meta.split("|")
            c = 0
            while c < metaList.__len__():
                data = metaList[c].split("//")
                key = data[0]
                metaDict.setdefault(key, [])
                value = data[1]
                metaDict[key].append(value)
                c += 1
        else:
            pass

        taxaDict = {}
        if all["taxa"]:
            taxa = all["taxa"]
            taxaList = taxa.split("|")
            taxaDict = {}
            c = 0
            while c < taxaList.__len__():
                data = taxaList[c].split("//")
                key = data[0]
                taxaDict.setdefault(key, [])
                value = data[1]
                taxaDict[key].append(value)
                c += 1
        else:
            pass

        finalList = []
        for rank in taxaDict:
            idList = taxaDict[rank]

            for id in idList:
                seriesDict = {}
                if (rank == 'Kingdom'):
                    name = Kingdom.objects.filter(**{'kingdomid': id}).values('kingdomName')
                    seriesDict["key"] = name[0]['kingdomName']
                elif (rank == 'Phyla'):
                    name = Phyla.objects.filter(**{'phylaid': id}).values('phylaName')
                    seriesDict["key"] = name[0]['phylaName']
                elif (rank == 'Class'):
                    name = Class.objects.filter(**{'classid': id}).values('className')
                    seriesDict["key"] = name[0]['className']
                elif (rank == 'Order'):
                    name = Order.objects.filter(**{'orderid': id}).values('orderName')
                    seriesDict["key"] = name[0]['orderName']
                elif (rank == 'Family'):
                    name = Family.objects.filter(**{'familyid': id}).values('familyName')
                    seriesDict["key"] = name[0]['familyName']
                elif (rank == 'Genus'):
                    name = Genus.objects.filter(**{'genusid': id}).values('genusName')
                    seriesDict["key"] = name[0]['genusName']
                elif (rank == 'Species'):
                    name = Species.objects.filter(**{'speciesid': id}).values('speciesName')
                    seriesDict["key"] = name[0]['speciesName']

                taxa_table = 'profile' + rank.lower() + '__' + rank.lower() + 'id'

                for field in metaDict:
                    valuesList = []
                    fieldList = metaDict[field]
                    table = ""
                    sampleTableList = ['sample_name', 'organism', 'seq_method', 'biome', 'feature', 'geo_loc', 'material']

                    for x in sampleTableList:
                        if field == x:
                            table = 'Sample'
                        else:
                            pass
                    collectTableList = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
                    for x in collectTableList:
                        if field == x:
                            table = 'Collect'
                        else:
                            pass
                    soil_classTableList = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
                    for x in soil_classTableList:
                        if field == x:
                            table = 'Soil_class'
                        else:
                            pass
                    mgtTableList = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
                    for x in mgtTableList:
                        if field == x:
                            table = 'Management'
                        else:
                            pass
                    usrTableList = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']
                    for x in usrTableList:
                        if field == x:
                            table = 'User'
                        else:
                            pass

                    annotate_field1 = 'profile' + rank.lower() + '__rel_abund'
                    annotate_field2 = 'profile' + rank.lower() + '__rich'
                    qs1 = Sample.objects.all().filter(sampleid__in=selected)
                    qs2 = qs1.filter(Q(**{taxa_table: id}))


                    if table == 'Sample':
                        args_list = []
                        for query in fieldList:
                            args_list.append(Q(**{field: query}))
                        qs3 = qs2.filter(reduce(operator.or_, args_list))
                        qs4 = qs3.values(field).annotate(count=Count(annotate_field1), ave_rel_abund=Avg(annotate_field1), ave_rich=Avg(annotate_field2))
                        for i in qs4:
                            valueDict = {
                                "label": i[field],
                                "ave_rel_abund": i['ave_rel_abund'],
                                "ave_rich": i['ave_rich'],
                                "count": i['count']
                            }
                            valuesList.append(valueDict)

                    elif table == 'Collect':
                        args_list = []
                        table_field = 'collect__' + str(field)
                        for query in fieldList:
                            args_list.append(Q(**{table_field: query}))
                        qs3 = qs2.filter(reduce(operator.or_, args_list))
                        qs4 = qs3.values(table_field).annotate(count=Count(annotate_field1), ave_rel_abund=Avg(annotate_field1), ave_rich=Avg(annotate_field2))
                        for i in qs4:
                            valueDict = {
                                "label": i[table_field],
                                "ave_rel_abund": i['ave_rel_abund'],
                                "ave_rich": i['ave_rich'],
                                "count": i['count']
                            }
                            valuesList.append(valueDict)

                    elif table == 'Soil_class':
                        args_list = []
                        table_field = 'soil_class__' + str(field)
                        for query in fieldList:
                            args_list.append(Q(**{table_field: query}))
                        qs3 = qs2.filter(reduce(operator.or_, args_list))
                        qs4 = qs3.values(table_field).annotate(count=Count(annotate_field1), ave_rel_abund=Avg(annotate_field1), ave_rich=Avg(annotate_field2))
                        for i in qs4:
                            valueDict = {
                                "label": i[table_field],
                                "ave_rel_abund": i['ave_rel_abund'],
                                "ave_rich": i['ave_rich'],
                                "count": i['count']
                            }
                            valuesList.append(valueDict)

                    elif table == 'Management':
                        args_list = []
                        table_field = 'management__' + str(field)
                        for query in fieldList:
                            args_list.append(Q(**{table_field: query}))
                        qs3 = qs2.filter(reduce(operator.or_, args_list))
                        qs4 = qs3.values(table_field).annotate(count=Count(annotate_field1), ave_rel_abund=Avg(annotate_field1), ave_rich=Avg(annotate_field2))
                        for i in qs4:
                            valueDict = {
                                "label": i[table_field],
                                "ave_rel_abund": i['ave_rel_abund'],
                                "ave_rich": i['ave_rich'],
                                "count": i['count']
                            }
                            valuesList.append(valueDict)

                    elif table == 'User':
                        args_list = []
                        table_field = 'user__' + str(field)
                        for query in fieldList:
                            args_list.append(Q(**{table_field: query}))
                        qs3 = qs2.filter(reduce(operator.or_, args_list))
                        qs4 = qs3.values(table_field).annotate(count=Count(annotate_field1), ave_rel_abund=Avg(annotate_field1), ave_rich=Avg(annotate_field2))
                        for i in qs4:
                            valueDict = {
                                "label": i[table_field],
                                "ave_rel_abund": i['ave_rel_abund'],
                                "ave_rich": i['ave_rich'],
                                "count": i['count']
                            }
                            valuesList.append(valueDict)

                    seriesDict["values"] = valuesList
                finalList.append(seriesDict)
        res = simplejson.dumps(finalList)
        return HttpResponse(res, content_type='application/json')


def getQuantGraphData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        metaDict = {}
        if all["meta"]:
            meta = all["meta"]
            metaList = meta.split("|")
            c = 0
            while c < metaList.__len__():
                data = metaList[c].split("//")
                key = data[0]
                metaDict.setdefault(key, [])
                value = data[1]
                metaDict[key].append(value)
                c += 1
        else:
            pass

        taxaDict = {}
        if all["taxa"]:
            taxa = all["taxa"]
            taxaList = taxa.split("|")
            taxaDict = {}
            c = 0
            while c < taxaList.__len__():
                data = taxaList[c].split("//")
                key = data[0]
                taxaDict.setdefault(key, [])
                value = data[1]
                taxaDict[key].append(value)
                c += 1
        else:
            pass

        finalList = []
        for rank in taxaDict:
            idList = taxaDict[rank]

            for id in idList:
                name = ""

                if (rank == 'Kingdom'):
                    qs = Kingdom.objects.filter(**{'kingdomid': id}).values('kingdomName')
                    name = qs[0]['kingdomName']
                if (rank == 'Phyla'):
                    qs = Phyla.objects.filter(**{'phylaid': id}).values('phylaName')
                    name = qs[0]['phylaName']
                if (rank == 'Class'):
                    qs = Class.objects.filter(**{'classid': id}).values('className')
                    name = qs[0]['className']
                if (rank == 'Order'):
                    qs = Order.objects.filter(**{'orderid': id}).values('orderName')
                    name = qs[0]['orderName']
                if (rank == 'Family'):
                    qs = Family.objects.filter(**{'familyid': id}).values('familyName')
                    name = qs[0]['familyName']
                if (rank == 'Genus'):
                    qs = Genus.objects.filter(**{'genusid': id}).values('genusName')
                    name = qs[0]['genusName']
                if (rank == 'Species'):
                    qs = Species.objects.filter(**{'speciesid': id}).values('speciesName')
                    name = qs[0]['speciesName']

                taxa_table = 'profile' + rank.lower() + '__' + rank.lower() + 'id'

                for category in metaDict:
                    fieldList = metaDict[category]
                    table = ""

                    if category == 'MIMARKs':
                        table = 'Sample'

                    if category == 'Sample Collection':
                        table = 'Collect'

                    if category == 'Climate':
                        table = 'Climate'

                    if category == 'Soil Classification':
                        table = 'Soil_class'

                    if category == 'Soil Nutrient':
                        table = 'Soil_nutrient'

                    if category == 'Microbial Biomass':
                        table = 'Microbial'

                    if category == 'User-defined':
                        table = 'User'

                    annotate_field1 = 'profile' + rank.lower() + '__rel_abund'
                    annotate_field2 = 'profile' + rank.lower() + '__rich'
                    qs1 = Sample.objects.all().filter(sampleid__in=selected)
                    qs2 = qs1.filter(Q(**{taxa_table: id}))

                    for field in fieldList:
                        valuesList = []

                        if table == 'Sample':
                            qs3 = qs2.values(field, 'sampleid', annotate_field1, annotate_field2)
                            for i in qs3:
                                tempDict = {}
                                tempDict['x'] = (i[field])
                                tempDict['y'] = (i[annotate_field1])
                                valuesList.append(tempDict)
                            valueDict = {
                                "key": name,
                                "values": valuesList,
                            }
                            finalList.append(valueDict)
                            print valueDict

                        if table == 'Climate':
                            table_field = 'climate__' + str(field)
                            qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                            for i in qs3:
                                tempDict = {}
                                tempDict['x'] = (i[table_field])
                                tempDict['y'] = (i[annotate_field1])
                                valuesList.append(tempDict)
                            valueDict = {
                                "key": name,
                                "values": valuesList,
                            }
                            finalList.append(valueDict)

                        if table == 'Collect':
                            table_field = 'collect__' + str(field)
                            qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                            for i in qs3:
                                tempDict = {}
                                tempDict['x'] = (i[table_field])
                                tempDict['y'] = (i[annotate_field1])
                                valuesList.append(tempDict)
                            valueDict = {
                                "key": name,
                                "values": valuesList,
                            }
                            finalList.append(valueDict)

                        if table == 'Soil_class':
                            table_field = 'collect__' + str(field)
                            qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                            for i in qs3:
                                tempDict = {}
                                tempDict['x'] = (i[table_field])
                                tempDict['y'] = (i[annotate_field1])
                                valuesList.append(tempDict)
                            valueDict = {
                                "key": name,
                                "values": valuesList,
                            }
                            finalList.append(valueDict)

                        elif table == 'User':
                            table_field = 'user__' + str(field)
                            qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                            for i in qs3:
                                tempDict = {}
                                tempDict['x'] = (i[table_field])
                                tempDict['y'] = (i[annotate_field1])
                                valuesList.append(tempDict)
                            valueDict = {
                                "key": name,
                                "values": valuesList,
                            }
                            finalList.append(valueDict)

                        elif table == 'Microbial':
                            table_field = 'microbial__' + str(field)
                            qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                            for i in qs3:
                                tempDict = {}
                                tempDict['x'] = (i[table_field])
                                tempDict['y'] = (i[annotate_field1])
                                valuesList.append(tempDict)
                            valueDict = {
                                "key": name,
                                "values": valuesList,
                            }
                            finalList.append(valueDict)

                        elif table == 'Soil_nutrient':
                            table_field = 'soil_nutrient__' + str(field)
                            qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                            for i in qs3:
                                tempDict = {}
                                tempDict['x'] = (i[table_field])
                                tempDict['y'] = (i[annotate_field1])
                                valuesList.append(tempDict)
                            valueDict = {
                                "key": name,
                                "values": valuesList,
                            }
                            finalList.append(valueDict)

            res = simplejson.dumps(finalList)
            return HttpResponse(res, content_type='application/json')

