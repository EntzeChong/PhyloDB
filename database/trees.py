import pickle
import simplejson
import operator
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q
from models import Project, Sample, Collect, Soil_class, Management, User
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile
from models import ProfileKingdom, ProfilePhyla, ProfileClass, ProfileOrder, ProfileFamily, ProfileGenus, ProfileSpecies
import pandas as pd
from scipy import stats
from numpy import *

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

    list = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc', 'material']
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


    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': False,  'hideCheckbox': True, 'expand': True, 'children': []}
    mimark = {'title': 'MIMARKs', 'tooltip': 'MIMARKs', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    collect = {'title': 'Sample Collection', 'tooltip': 'Sample Collection', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    climate = {'title': 'Climate', 'tooltip': 'Climate', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_class = {'title': 'Soil Classification', 'tooltip': 'Soil Classification', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_nutrient = {'title': 'Soil Nutrient', 'tooltip': 'Soil Nutrient', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    microbial = {'title': 'Microbial Biomass', 'tooltip': 'Microbial Biomass', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    user = {'title': 'User-defined', 'tooltip': 'User_defined', 'isFolder': True,  'hideCheckbox': True, 'children': []}

    list = ['lat_lon', 'elevation']
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

        idList = []
        if all["taxa"]:
            taxa = all["taxa"]
            idList = taxa.split("|")

        kingdomList = Kingdom.objects.values_list('kingdomid', flat=True)
        phylaList = Phyla.objects.values_list('phylaid', flat=True)
        classList = Class.objects.values_list('classid', flat=True)
        orderList = Order.objects.values_list('orderid', flat=True)
        familyList = Family.objects.values_list('familyid', flat=True)
        genusList = Genus.objects.values_list('genusid', flat=True)
        speciesList = Species.objects.values_list('speciesid', flat=True)

        df = pd.DataFrame(columns=['taxa', 'table', 'field', 'x_value', 'abund', 'rich'])
        for id in idList:
            name = ""
            taxa_table = ""
            annotate_field1 = ""
            annotate_field2 = ""

            if id in kingdomList:
                qs = Kingdom.objects.filter(**{'kingdomid': id}).values('kingdomName')
                name = qs[0]['kingdomName']
                taxa_table = 'profilekingdom__kingdomid'
                annotate_field1 = 'profilekingdom__rel_abund'
                annotate_field2 = 'profilekingdom__rich'
            elif id in phylaList:
                qs = Phyla.objects.filter(**{'phylaid': id}).values('phylaName')
                name = qs[0]['phylaName']
                taxa_table = 'profilephyla__phylaid'
                annotate_field1 = 'profilephyla__rel_abund'
                annotate_field2 = 'profilephyla__rich'
            elif id in classList:
                qs = Class.objects.filter(**{'classid': id}).values('className')
                name = qs[0]['className']
                taxa_table = 'profileclass__classid'
                annotate_field1 = 'profileclass__rel_abund'
                annotate_field2 = 'profileclass__rich'
            elif id in orderList:
                qs = Order.objects.filter(**{'orderid': id}).values('orderName')
                name = qs[0]['orderName']
                taxa_table = 'profileorder__orderid'
                annotate_field1 = 'profileorder__rel_abund'
                annotate_field2 = 'profileorder__rich'
            elif id in familyList:
                qs = Family.objects.filter(**{'familyid': id}).values('familyName')
                name = qs[0]['familyName']
                taxa_table = 'profilefamily__familyid'
                annotate_field1 = 'profilefamily__rel_abund'
                annotate_field2 = 'profilefamily__rich'
            elif id in genusList:
                qs = Genus.objects.filter(**{'genusid': id}).values('genusName')
                name = qs[0]['genusName']
                taxa_table = 'profilegenus__genusid'
                annotate_field1 = 'profilegenus__rel_abund'
                annotate_field2 = 'profilegenus__rich'
            elif id in speciesList:
                qs = Species.objects.filter(**{'speciesid': id}).values('speciesName')
                name = qs[0]['speciesmName']
                taxa_table = 'profilespecies__speciesid'
                annotate_field1 = 'profilespecies__rel_abund'
                annotate_field2 = 'profilespecies__rich'

            for category in metaDict:
                fieldList = metaDict[category]
                table = ""

                sampleTableList = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc', 'material']
                collectTableList = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
                soil_classTableList = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
                mgtTableList = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
                usrTableList = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']

                if category in sampleTableList:
                    table = 'Sample'

                if category in collectTableList:
                    table = 'Collect'

                if category in soil_classTableList:
                    table = 'Soil_class'

                if category in mgtTableList:
                    table = 'Management'

                if category in usrTableList:
                    table = 'User'

                qs1 = Sample.objects.all().filter(sampleid__in=selected)
                qs2 = qs1.filter(Q(**{taxa_table: id}))

                if table == 'Sample':
                    args_list = []
                    for query in fieldList:
                        args_list.append(Q(**{category: query}))
                    qs3 = qs2.filter(reduce(operator.or_, args_list)).values(category, annotate_field1, annotate_field2)
                    for i in qs3:
                        df.loc[len(df)+1] = [str(name), str(table), str(category), str(i[category]), float(i[annotate_field1]), int(i[annotate_field2])]

                elif table == 'Collect':
                    args_list = []
                    table_category = 'collect__' + str(category)
                    for query in fieldList:
                        args_list.append(Q(**{table_category: query}))
                    qs3 = qs2.filter(reduce(operator.or_, args_list)).values(table_category, annotate_field1, annotate_field2)
                    for i in qs3:
                        df.loc[len(df)+1] = [str(name), str(table), str(category), str(i[table_category]), float(i[annotate_field1]), int(i[annotate_field2])]

                elif table == 'Soil_class':
                    args_list = []
                    table_category = 'soil-class__' + str(category)
                    for query in fieldList:
                        args_list.append(Q(**{table_category: query}))
                    qs3 = qs2.filter(reduce(operator.or_, args_list)).values(table_category, annotate_field1, annotate_field2)
                    for i in qs3:
                        df.loc[len(df)+1] = [str(name), str(table), str(category), str(i[table_category]), float(i[annotate_field1]), int(i[annotate_field2])]

                elif table == 'Management':
                    args_list = []
                    table_category = 'management__' + str(category)
                    for query in fieldList:
                        args_list.append(Q(**{table_category: query}))
                    qs3 = qs2.filter(reduce(operator.or_, args_list)).values(table_category, annotate_field1, annotate_field2)
                    for i in qs3:
                        df.loc[len(df)+1] = [str(name), str(table), str(category), str(i[table_category]), float(i[annotate_field1]), int(i[annotate_field2])]

                elif table == 'User':
                    args_list = []
                    table_category = 'user__' + str(category)
                    for query in fieldList:
                        args_list.append(Q(**{table_category: query}))
                    qs3 = qs2.filter(reduce(operator.or_, args_list)).values(table_category, annotate_field1, annotate_field2)
                    for i in qs3:
                        df.loc[len(df)+1] = [str(name), str(table), str(category), str(i[table_category]), float(i[annotate_field1]), int(i[annotate_field2])]

        finalDict = {'abund': [], 'rich': []}
        abundList = []
        richList = []

        print df
        grouped1 = df.groupby(['taxa', 'table', 'field'])
        for name1, group1 in grouped1:
            abundSeriesDict = {}
            abundValuesList = []
            richSeriesDict = {}
            richValuesList = []

            values_per_group = [col for col_name, col in group1.groupby('x_value')['abund']]
            try:
                abund_f_val, abund_p_val = stats.f_oneway(*values_per_group)
            except:
                abund_f_val = 'NaN'
                abund_p_val = 'NaN'
            values_per_group = [col for col_name, col in group1.groupby('x_value')['rich']]
            try:
                rich_f_val, rich_p_val = stats.f_oneway(*values_per_group)
            except:
                rich_f_val = 'NaN'
                rich_p_val = 'NaN'

            grouped2 = group1.groupby('x_value')
            for name2, group2 in grouped2:
                abundValueDict = {}
                richValueDict = {}

                abund_mean = group2['abund'].mean()
                abund_std = group2['abund'].std()
                if isnan(abund_std):
                    abund_std = 0
                rich_mean = group2['rich'].mean()
                rich_std = group2['rich'].std()
                if isnan(rich_std):
                    rich_std = 0

                abundValueDict['label'] = name2
                abundValueDict['value'] = abund_mean
                abundValueDict['stdev'] = abund_std
                abundValuesList.append(abundValueDict)

                richValueDict['label'] = name2
                richValueDict['value'] = rich_mean
                richValueDict['stdev'] = rich_std
                richValuesList.append(richValueDict)

            abundSeriesDict['key'] = name1[0]
            abundSeriesDict['table'] = name1[1]
            abundSeriesDict['field'] = name1[2]
            abundSeriesDict['f_value'] = abund_f_val
            abundSeriesDict['p_value'] = abund_p_val
            abundSeriesDict['values'] = abundValuesList

            richSeriesDict['key'] = name1[0]
            richSeriesDict['table'] = name1[1]
            richSeriesDict['field'] = name1[2]
            richSeriesDict['f_value'] = rich_f_val
            richSeriesDict['p_value'] = rich_p_val
            richSeriesDict['values'] = richValuesList

            abundList.append(abundSeriesDict)
            richList.append(richSeriesDict)

        finalDict['abund'] = abundList
        finalDict['rich'] = richList

        print finalDict
        res = simplejson.dumps(finalDict)
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

        idList = []
        if all["taxa"]:
            taxa = all["taxa"]
            idList = taxa.split("|")

        kingdomList = Kingdom.objects.values_list('kingdomid', flat=True)
        phylaList = Phyla.objects.values_list('phylaid', flat=True)
        classList = Class.objects.values_list('classid', flat=True)
        orderList = Order.objects.values_list('orderid', flat=True)
        familyList = Family.objects.values_list('familyid', flat=True)
        genusList = Genus.objects.values_list('genusid', flat=True)
        speciesList = Species.objects.values_list('speciesid', flat=True)

        df = pd.DataFrame(columns=['taxa', 'field', 'x', 'y_abund', 'y_rich'])
        for id in idList:
            name = ""
            taxa_table = ""
            annotate_field1 = ""
            annotate_field2 = ""

            if id in kingdomList:
                qs = Kingdom.objects.filter(**{'kingdomid': id}).values('kingdomName')
                name = qs[0]['kingdomName']
                taxa_table = 'profilekingdom__kingdomid'
                annotate_field1 = 'profilekingdom__rel_abund'
                annotate_field2 = 'profilekingdom__rich'
            elif id in phylaList:
                qs = Phyla.objects.filter(**{'phylaid': id}).values('phylaName')
                name = qs[0]['phylaName']
                taxa_table = 'profilephyla__phylaid'
                annotate_field1 = 'profilephyla__rel_abund'
                annotate_field2 = 'profilephyla__rich'
            elif id in classList:
                qs = Class.objects.filter(**{'classid': id}).values('className')
                name = qs[0]['className']
                taxa_table = 'profileclass__classid'
                annotate_field1 = 'profileclass__rel_abund'
                annotate_field2 = 'profileclass__rich'
            elif id in orderList:
                qs = Order.objects.filter(**{'orderid': id}).values('orderName')
                name = qs[0]['orderName']
                taxa_table = 'profileorder__orderid'
                annotate_field1 = 'profileorder__rel_abund'
                annotate_field2 = 'profileorder__rich'
            elif id in familyList:
                qs = Family.objects.filter(**{'familyid': id}).values('familyName')
                name = qs[0]['familyName']
                taxa_table = 'profilefamily__familyid'
                annotate_field1 = 'profilefamily__rel_abund'
                annotate_field2 = 'profilefamily__rich'
            elif id in genusList:
                qs = Genus.objects.filter(**{'genusid': id}).values('genusName')
                name = qs[0]['genusName']
                taxa_table = 'profilegenus__genusid'
                annotate_field1 = 'profilegenus__rel_abund'
                annotate_field2 = 'profilegenus__rich'
            elif id in speciesList:
                qs = Species.objects.filter(**{'speciesid': id}).values('speciesName')
                name = qs[0]['speciesmName']
                taxa_table = 'profilespecies__speciesid'
                annotate_field1 = 'profilespecies__rel_abund'
                annotate_field2 = 'profilespecies__rich'

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

                qs1 = Sample.objects.all().filter(sampleid__in=selected)
                qs2 = qs1.filter(Q(**{taxa_table: id}))

                for field in fieldList:
                    if table == 'Sample':
                        qs3 = qs2.values(field, 'sampleid', annotate_field1, annotate_field2)
                        for i in qs3:
                            df.loc[len(df)+1] = [str(name), str(field), int(i[field]), float(i[annotate_field1]), int(i[annotate_field2])]

                    if table == 'Climate':
                        table_field = 'climate__' + str(field)
                        qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                        for i in qs3:
                            df.loc[len(df)+1] = [str(name), str(field), int(i[table_field]), float(i[annotate_field1]), int(i[annotate_field2])]

                    if table == 'Collect':
                        table_field = 'collect__' + str(field)
                        qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                        for i in qs3:
                            df.loc[len(df)+1] = [str(name), str(field), int(i[table_field]), float(i[annotate_field1]), int(i[annotate_field2])]

                    if table == 'Soil_class':
                        table_field = 'collect__' + str(field)
                        qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                        for i in qs3:
                            df.loc[len(df)+1] = [str(name), str(field), int(i[table_field]), float(i[annotate_field1]), int(i[annotate_field2])]

                    elif table == 'User':
                        table_field = 'user__' + str(field)
                        qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                        for i in qs3:
                            df.loc[len(df)+1] = [str(name), str(field), int(i[table_field]), float(i[annotate_field1]), int(i[annotate_field2])]

                    elif table == 'Microbial':
                        table_field = 'microbial__' + str(field)
                        qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                        for i in qs3:
                            df.loc[len(df)+1] = [str(name), str(field), int(i[table_field]), float(i[annotate_field1]), int(i[annotate_field2])]

                    elif table == 'Soil_nutrient':
                        table_field = 'soil_nutrient__' + str(field)
                        qs3 = qs2.values(table_field, 'sampleid', annotate_field1, annotate_field2)
                        for i in qs3:
                            df.loc[len(df)+1] = [str(name), str(field), int(i[table_field]), float(i[annotate_field1]), int(i[annotate_field2])]

        finalDict = {'abund': [], 'rich': []}
        abundList = []
        richList = []
        grouped = df.groupby(['taxa', 'field'])
        for name, group in grouped:
            abund_slope, abund_intercept, abund_r_value, abund_p_value, abund_std_err = stats.linregress(group['x'], group['y_abund'])
            pred_y_abund = abund_intercept + abund_slope * group['x']
            abund_r_sq = abund_r_value * abund_r_value
            rich_slope, rich_intercept, rich_r_value, rich_p_value, rich_std_err = stats.linregress(group['x'], group['y_rich'])
            pred_y_rich = rich_intercept + rich_slope * group['x']
            rich_r_sq = rich_r_value * rich_r_value

            group['pred_y_abund'] = pred_y_abund
            group['abund_r_sq'] = abund_r_sq
            group['pred_y_rich'] = pred_y_rich
            group['rich_r_sq'] = rich_r_sq

            abundSeriesDict = {}
            abundValuesList = []
            richSeriesDict = {}
            richValuesList = []
            for index, row in group.iterrows():
                abundValueDict = {}
                richValueDict = {}

                abundValueDict['x'] = row['x']
                abundValueDict['y_abund'] = row['y_abund']
                abundValueDict['pred_y_abund'] = row['pred_y_abund']
                abundValuesList.append(abundValueDict)

                richValueDict['x'] = row['x']
                richValueDict['y_rich'] = row['y_rich']
                richValueDict['pred_y_rich'] = row['pred_y_rich']
                richValuesList.append(richValueDict)

            abundSeriesDict['key'] = name[0]
            abundSeriesDict['x-label'] = name[1]
            abundSeriesDict['r_square'] = abund_r_sq
            abundSeriesDict['p_value'] = abund_p_value
            abundSeriesDict['std_err'] = abund_std_err
            abundSeriesDict['slope'] = abund_slope
            abundSeriesDict['intercept'] = abund_intercept
            abundSeriesDict['values'] = abundValuesList

            richSeriesDict['key'] = name[0]
            richSeriesDict['x-label'] = name[1]
            richSeriesDict['r_square'] = rich_r_sq
            richSeriesDict['p_value'] = rich_p_value
            richSeriesDict['std_err'] = rich_std_err
            richSeriesDict['slope'] = rich_slope
            richSeriesDict['intercept'] = rich_intercept
            richSeriesDict['values'] = richValuesList

            abundList.append(abundSeriesDict)
            richList.append(richSeriesDict)

            finalDict['abund'] = abundList
            finalDict['rich'] = richList

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')


