import pickle
import collections
import simplejson
import operator
import pandas as pd
import numpy as np
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q
from models import Project, Sample, Collect, Soil_class, Management, User
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile
from models import ProfileKingdom, ProfilePhyla, ProfileClass, ProfileOrder, ProfileFamily, ProfileGenus, ProfileSpecies
from utils import multidict
from scipy import stats
from numpy import *
from pyvttbl import Anova1way
from scipy.stats import linregress

def getProjectTree(request):
    myTree = {'title': 'All Projects', 'isFolder': True, 'expand': True, 'hideCheckbox': True, 'children': []}

    projects = Project.objects.all()

    for project in projects:
        myNode = {
            'title': project.project_name,
            'tooltip': project.project_desc,
            'id': project.projectid,
            'isFolder': True,
            'isLazy': True
        }
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


def getProjectTreeChildren(request):
    if request.is_ajax():
        projectid = request.GET["id"]
        samples = Sample.objects.filter(projectid=projectid)

        nodes = []
        for sample in samples:
            myNode = {
                'title': sample.sample_name,
                'tooltip': sample.title,
                'id': sample.sampleid,
                'isFolder': False
            }
            nodes.append(myNode)

        res = simplejson.dumps(nodes, encoding="Latin-1")
        return StreamingHttpResponse(res, content_type='application/json')


def getSampleCatTree(request):
    myTree = {'title': 'root', 'tooltip': 'root', 'isFolder': False,  'hideCheckbox': True, 'expand': True, 'children': []}
    mimark = {'title': 'MIMARKs', 'tooltip': 'MIMARKs', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    collect = {'title': 'Sample Collection', 'tooltip': 'Sample Collection', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_class = {'title': 'Soil Classification', 'tooltip': 'Soil Classification', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    management = {'title': 'Management', 'tooltip': 'Management', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    user = {'title': 'User-defined', 'tooltip': 'User_defined', 'isFolder': True,  'hideCheckbox': True, 'children': []}

    list = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc', 'material']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'MIMARKs', 'isFolder': True, 'id': 'mimark', 'isLazy': True}
        mimark['children'].append(myNode)

    list = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'Sample Collection', 'isFolder': True, 'id': 'collect', 'isLazy': True}
        collect['children'].append(myNode)

    list = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'Soil Classification', 'isFolder': True, 'id': 'soil_class', 'isLazy': True}
        soil_class['children'].append(myNode)

    list = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
    for i in range(len(list)):
        myNode = {'title': list[i],  'tooltip': 'Management', 'isFolder': True, 'id': 'management', 'isLazy': True}
        management['children'].append(myNode)

    list = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'User-defined', 'isFolder': True, 'id': 'user', 'isLazy': True}
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


def getSampleCatTreeChildren(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')

    if request.is_ajax():
        table = request.GET["table"]
        field = request.GET["field"]
        nodes = []

        if table == 'mimark':
            items = Sample.objects.values_list(field, flat='True').filter(sampleid__in=selected).distinct()
            for j in items:
                myNode = {
                    'title': j,
                    'id': j,
                    'tooltip': field,
                    'isFolder': False
                }
                nodes.append(myNode)

        elif table == 'collect':
            items = Collect.objects.values_list(field, flat='True').filter(sampleid_id__in=selected).distinct()
            for j in items:
                myNode = {
                    'title': j,
                    'id': j,
                    'tooltip': field,
                    'isFolder': False
                }
                nodes.append(myNode)

        elif table == 'soil_class':
            items = Soil_class.objects.values_list(field, flat='True').filter(sampleid_id__in=selected).distinct()
            for j in items:
                myNode = {
                    'title': j,
                    'id': j,
                    'tooltip': field,
                    'isFolder': False
                }
                nodes.append(myNode)

        elif table == 'management':
            items = Management.objects.values_list(field, flat='True').filter(sampleid_id__in=selected).distinct()
            for j in items:
                myNode = {
                    'title': j,
                    'id': j,
                    'tooltip': field,
                    'isFolder': False
                }
                nodes.append(myNode)

        elif table == 'user':
            items = User.objects.values_list(field, flat='True').filter(sampleid_id__in=selected).distinct()
            for j in items:
                myNode = {
                    'title': j,
                    'id': j,
                    'tooltip': field,
                    'isFolder': False
                }
                nodes.append(myNode)

        res = simplejson.dumps(nodes, encoding="Latin-1")
        return StreamingHttpResponse(res, content_type='application/json')


def getSampleQuantTree(request):
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
        myNode = {'title': list[i], 'isFolder': True, 'id': 'mimark'}
        mimark['children'].append(myNode)

    list = ['samp_size', 'samp_weight_dna_ext']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'id': 'collect'}
        collect['children'].append(myNode)

    list = ['annual_season_precpt', 'annual_season_temp']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'id': 'climate'}
        climate['children'].append(myNode)

    list = ['bulk_density', 'porosity', 'slope_gradient', 'water_content_soil']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'id': 'soil_class'}
        soil_class['children'].append(myNode)

    list = ['pH', 'EC', 'tot_C', 'tot_OM', 'tot_N', 'NO3_N', 'NH4_N', 'P', 'K', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'Ca', 'Mg', 'Na', 'B']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'id': 'soil_nutrient'}
        soil_nutrient['children'].append(myNode)

    list = ['rRNA_copies', 'microbial_biomass_C', 'microbial_biomass_N', 'microbial_respiration']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'id': 'microbial'}
        microbial['children'].append(myNode)

    list = ['usr_quant1', 'usr_quant2', 'usr_quant3', 'usr_quant4', 'usr_quant5', 'usr_quant6']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'id': 'user'}
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

    for kingdom in kingdoms:
        myNode = {
            'title': kingdom.kingdomName,
            'id': kingdom.kingdomid,
            'tooltip': "Kingdom",
            'isFolder': True,
            'expand': True,
            'children': []
        }
        phylas = kingdom.phyla_set.filter(phylaid__in=selected_taxa.values_list('phylaid')).order_by('phylaName')
        for phyla in phylas:
            myNode1 = {
                'title': phyla.phylaName,
                'id': phyla.phylaid,
                'tooltip': "Phyla",
                'isFolder': True,
                'isLazy': True
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


def getTaxaTreeChildren(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    selected_taxa = Profile.objects.filter(sampleid_id__in=selected)

    if request.is_ajax():
        taxa = request.GET["tooltip"]
        id = request.GET["id"]

        nodes = []
        if taxa == 'Phyla':
            qs = Class.objects.filter(classid__in=selected_taxa.values_list('classid')).filter(**{'phylaid': id}).order_by('className')
            for item in qs:
                myNode = {
                    'title': item.className,
                    'id': item.classid,
                    'tooltip': "Class",
                    'isFolder': True,
                    'isLazy': True
                }
                nodes.append(myNode)

        elif taxa == 'Class':
            qs = Order.objects.filter(orderid__in=selected_taxa.values_list('orderid')).filter(**{'classid': id}).order_by('orderName')
            for item in qs:
                myNode = {
                    'title': item.orderName,
                    'id': item.orderid,
                    'tooltip': "Order",
                    'isFolder': True,
                    'isLazy': True
                }
                nodes.append(myNode)

        elif taxa == 'Order':
            qs = Family.objects.filter(familyid__in=selected_taxa.values_list('familyid')).filter(**{'orderid': id}).order_by('familyName')
            for item in qs:
                myNode = {
                    'title': item.familyName,
                    'id': item.familyid,
                    'tooltip': "Family",
                    'isFolder': True,
                    'isLazy': True
                }
                nodes.append(myNode)

        elif taxa == 'Family':
            qs = Genus.objects.filter(genusid__in=selected_taxa.values_list('genusid')).filter(**{'familyid': id}).order_by('genusName')
            for item in qs:
                myNode = {
                    'title': item.genusName,
                    'id': item.genusid,
                    'tooltip': "Genus",
                    'isFolder': True,
                    'isLazy': True
                }
                nodes.append(myNode)

        elif taxa == 'Genus':
            qs = Species.objects.filter(speciesid__in=selected_taxa.values_list('speciesid')).filter(**{'genusid': id}).order_by('speciesName')
            for item in qs:
                myNode = {
                    'title': item.speciesName,
                    'id': item.speciesid,
                    'tooltip': "Species",
                }
                nodes.append(myNode)

        res = simplejson.dumps(nodes, encoding="Latin-1")
        return StreamingHttpResponse(res, content_type='application/json')


def getCatGraphData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    qs1 = Sample.objects.all().filter(sampleid__in=selected)

    sampleTableList = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc', 'material']
    collectTableList = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
    soil_classTableList = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
    mgtTableList = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
    usrTableList = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        taxaString = all["taxa"]
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        finalDF = pd.DataFrame()
        metaDF = pd.DataFrame()
        final_fieldList = []
        for key, value in metaDict.items():
            args_list = []
            field_list = []

            if key in sampleTableList:
                field_list.append('sampleid')
                field = str(key)
                final_fieldList.append(key)
                field_list.append(field)
                if type(value) is unicode:
                    args_list.append(Q(**{field: value}))
                else:
                    for item in value:
                        args_list.append(Q(**{field: item}))
                qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key in collectTableList:
                field_list.append('sampleid')
                field = 'collect__' + str(key)
                field_list.append(field)
                final_fieldList.append(key)
                if type(value) is unicode:
                    args_list.append(Q(**{field: value}))
                else:
                    for item in value:
                        args_list.append(Q(**{field: item}))
                qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: key}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key in soil_classTableList:
                field_list.append('sampleid')
                field = 'soil_class__' + str(key)
                field_list.append(field)
                final_fieldList.append(key)
                if type(value) is unicode:
                    args_list.append(Q(**{field: value}))
                else:
                    for item in value:
                        args_list.append(Q(**{field: item}))
                qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: key}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key in mgtTableList:
                field_list.append('sampleid')
                field = 'management__' + str(key)
                field_list.append(field)
                final_fieldList.append(key)
                if type(value) is unicode:
                    args_list.append(Q(**{field: value}))
                else:
                    for item in value:
                        args_list.append(Q(**{field: item}))
                qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: key}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key in usrTableList:
                field_list.append('sampleid')
                field = 'user__' + str(key)
                field_list.append(field)
                final_fieldList.append(key)
                if type(value) is unicode:
                    args_list.append(Q(**{field: value}))
                else:
                    for item in value:
                        args_list.append(Q(**{field: item}))
                qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: key}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

        graph_selected = metaDF['sampleid'].tolist()
        myset = list(set(graph_selected))

        ## Filter the taxonomy profile tables
        for key, value in taxaDict.items():
            if type(value) is unicode:
                if key == 'Kingdom':
                    field = 'kingdomid'
                    qs1 = ProfileKingdom.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'kingdomid', 'kingdomid__kingdomName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'kingdomid', 'kingdomid__kingdomName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Kingdom'
                    taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Kingdom', inplace=True)
                    name = Kingdom.objects.filter(Q(**{'kingdomid': value})).values('kingdomid', 'kingdomName')
                    mergeDF['taxa_id'].fillna(name[0]['kingdomid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['kingdomName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Phyla':
                    field = 'phylaid'
                    qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Phyla'
                    taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Phyla', inplace=True)
                    name = Phyla.objects.filter(Q(**{'phylaid': value})).values('phylaid', 'phylaName')
                    mergeDF['taxa_id'].fillna(name[0]['phylaid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['phylaName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Class':
                    field = 'classid'
                    qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'classid', 'classid__className', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Class'
                    taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Class', inplace=True)
                    name = Class.objects.filter(Q(**{'classid': value})).values('classid', 'className')
                    mergeDF['taxa_id'].fillna(name[0]['classid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['className'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Order':
                    field = 'orderid'
                    qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Order'
                    taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Order', inplace=True)
                    name = Order.objects.filter(Q(**{'orderid': value})).values('orderid', 'orderName')
                    mergeDF['taxa_id'].fillna(name[0]['orderid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['orderName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Family':
                    field = 'familyid'
                    qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Famiily'
                    taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Family', inplace=True)
                    name = Family.objects.filter(Q(**{'familyid': value})).values('familyid', 'familyName')
                    mergeDF['taxa_id'].fillna(name[0]['familyid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['familyName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Genus':
                    field = 'genusid'
                    qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Genus'
                    taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Genus', inplace=True)
                    name = Genus.objects.filter(Q(**{'genusid': value})).values('genusid', 'genusName')
                    mergeDF['taxa_id'].fillna(name[0]['genusid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['genusName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Species':
                    field = 'speciesid'
                    qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values()
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Species'
                    taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Species', inplace=True)
                    name = Kingdom.objects.filter(Q(**{'speciesid': value})).values('speciesid', 'speciesName')
                    mergeDF['taxa_id'].fillna(name[0]['speciesid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['speciesName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

            elif type(value) is list:
                if key == 'Kingdom':
                    for item in value:
                        field = 'kingdomid'
                        qs1 = ProfileKingdom.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'kingdomid', 'kingdomid__kingdomName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'kingdomid', 'kingdomid__kingdomName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Kingdom'
                        taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Kingdom', inplace=True)
                        name = Kingdom.objects.filter(Q(**{'kingdomid': item})).values('kingdomid', 'kingdomName')
                        mergeDF['taxa_id'].fillna(name[0]['kingdomid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['kingdomName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Phyla':
                    for item in value:
                        field = 'phylaid'
                        qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Phyla'
                        taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Phyla', inplace=True)
                        name = Phyla.objects.filter(Q(**{'phylaid': item})).values('phylaid', 'phylaName')
                        mergeDF['taxa_id'].fillna(name[0]['phylaid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['phylaName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Class':
                    for item in value:
                        field = 'classid'
                        qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'classid', 'classid__className', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Class'
                        taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Class', inplace=True)
                        name = Class.objects.filter(Q(**{'classid': item})).values('classid', 'className')
                        mergeDF['taxa_id'].fillna(name[0]['classid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['className'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Order':
                    for item in value:
                        field = 'orderid'
                        qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Order'
                        taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Order', inplace=True)
                        name = Order.objects.filter(Q(**{'orderid': item})).values('orderid', 'orderName')
                        mergeDF['taxa_id'].fillna(name[0]['orderid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['orderName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Family':
                    for item in value:
                        field = 'familyid'
                        qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Family'
                        taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Family', inplace=True)
                        name = Family.objects.filter(Q(**{'familyid': item})).values('familyid', 'familyName')
                        mergeDF['taxa_id'].fillna(name[0]['familyid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['familyName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Genus':
                    for item in value:
                        field = 'genusid'
                        qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Genus'
                        taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Genus', inplace=True)
                        name = Genus.objects.filter(Q(**{'genusid': item})).values('genusid', 'genusName')
                        mergeDF['taxa_id'].fillna(name[0]['genusid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['genusName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Species':
                    for item in value:
                        field = 'speciesid'
                        qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Species'
                        taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Species', inplace=True)
                        name = Species.objects.filter(Q(**{'speciesid': item})).values('speciesid', 'speciesName')
                        mergeDF['taxa_id'].fillna(name[0]['speciesid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['speciesName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

        # Set datatypes
        finalDF[['rich', 'rel_abund']] = finalDF[['rich', 'rel_abund']].astype(float)

        finalDict = {'abund': [], 'rich': []}
        abundList = []
        richList = []

        grouped1 = finalDF.groupby(['taxa_id', 'taxa', 'taxa_name'])
        for name1, group1 in grouped1:
            abundValuesList = []
            richValuesList = []
            abundSeriesDict = {}
            richSeriesDict = {}
            abundValueDict = {}
            richValueDict = {}

            # Anova1way
            for field in final_fieldList:
                trtList = []
                valList = []
                grouped2 = group1.groupby(field)['rel_abund']
                for name, group in grouped2:
                    trtList.append(name)
                    valList.append(list(group.T))

                # Relative Abundance
                try:
                    D = Anova1way()
                    D.run(valList, conditions_list=trtList)
                    print 'Taxa level: ', name1[1]
                    print 'Taxa name: ', name1[2]
                    print 'Dependent Variable: Relative abundance'
                    print 'Independent Variable: ', field
                    print D
                    print '\n\n'
                except:
                    aov = 'ANOVA cannot be performed'
                    print 'Taxa level: ', name1[1]
                    print 'Taxa name: ', name1[2]
                    print 'Dependent Variable: Relative abundance'
                    print 'Independent Variable: ', field
                    print aov
                    print '\n\n'

                # Richness
                del trtList[:]  # empty list
                del valList[:]  # empty list
                grouped2 = group1.groupby(field)['rich']
                for name, group in grouped2:
                    trtList.append(name)
                    valList.append(list(group.T))
                try:
                    D = Anova1way()
                    D.run(valList, conditions_list=trtList)
                    print 'Taxa level: ', name1[1]
                    print 'Taxa name: ', name1[2]
                    print 'Dependent Variable: OTU richness'
                    print 'Independent Variable: ', field
                    print D
                    print '\n\n'
                except:
                    aov = 'ANOVA cannot be performed'
                    print 'Taxa level: ', name1[1]
                    print 'Taxa name: ', name1[2]
                    print 'Dependent Variable: Relative abundance'
                    print 'Independent Variable: ', field
                    print aov
                    print '\n\n'

            for field in final_fieldList:
                grouped2 = group1.groupby(field)
                for name2, group2 in grouped2:
                    abund_mean = group2['rel_abund'].mean()
                    abund_std = group2['rel_abund'].std()
                    abund_count = group2['rel_abund'].count()
                    if isnan(abund_std):
                        abund_std = 0
                    rich_mean = group2['rich'].mean()
                    rich_std = group2['rich'].std()
                    rich_count = group2['rich'].count()
                    if isnan(rich_std):
                        rich_std = 0

                    abundValueDict['label'] = name2
                    abundValueDict['value'] = abund_mean
                    abundValueDict['stdev'] = abund_std
                    abundValueDict['n'] = abund_count

                    richValueDict['label'] = name2
                    richValueDict['value'] = rich_mean
                    richValueDict['stdev'] = rich_std
                    abundValueDict['n'] = rich_count

                    abundValuesList.append(abundValueDict.copy())
                    richValuesList.append(richValueDict.copy())

            abundSeriesDict['key'] = name1[1] + ': ' + name1[2]
            abundSeriesDict['values'] = abundValuesList

            richSeriesDict['key'] = name1[1] + ': ' + name1[2]
            richSeriesDict['values'] = richValuesList

            abundList.append(abundSeriesDict.copy())
            richList.append(richSeriesDict.copy())

        finalDict['abund'] = abundList
        finalDict['rich'] = richList

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')


def getQuantGraphData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    qs1 = Sample.objects.all().filter(sampleid__in=selected)

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        taxaString = all["taxa"]
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        finalDF = pd.DataFrame()
        metaDF = pd.DataFrame()
        final_fieldList = []
        for key, value in metaDict.items():
            field_list = []

            if key == 'mimark':
                field_list.append('sampleid')
                field_list.append(value)
                final_fieldList.append(value)
                qs2 = qs1.values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={value: 'x-value'}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key == 'collect':
                field_list.append('sampleid')
                field = 'collect__' + str(value)
                field_list.append(field)
                final_fieldList.append(value)
                qs2 = qs1.values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: 'x-value'}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key == 'climate':
                field_list.append('sampleid')
                field = 'climate__' + str(value)
                field_list.append(field)
                final_fieldList.append(value)
                qs2 = qs1.values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: 'x-value'}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key == 'soil_class':
                field_list.append('sampleid')
                field = 'soil_class__' + str(value)
                field_list.append(field)
                final_fieldList.append(value)
                qs2 = qs1.values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: 'x-value'}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key == 'soil_nutrient':
                field_list.append('sampleid')
                field = 'soil_nutrient__' + str(value)
                field_list.append(field)
                final_fieldList.append(value)
                qs2 = qs1.values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: 'x-value'}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key == 'microbial':
                field_list.append('sampleid')
                field = 'microbial__' + str(value)
                field_list.append(field)
                final_fieldList.append(value)
                qs2 = qs1.values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: 'x-value'}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

            elif key == 'user':
                field_list.append('sampleid')
                field = 'user__' + str(value)
                field_list.append(field)
                final_fieldList.append(value)
                qs2 = qs1.values(*field_list)
                tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
                tempDF.rename(columns={field: 'x-value'}, inplace=True)
                if metaDF.empty:
                    metaDF = tempDF
                else:
                    metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

        graph_selected = metaDF['sampleid'].tolist()
        myset = list(set(graph_selected))

        ## Filter the taxonomy profile tables
        for key, value in taxaDict.items():
            if type(value) is unicode:
                if key == 'Kingdom':
                    field = 'kingdomid'
                    qs1 = ProfileKingdom.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'kingdomid', 'kingdomid__kingdomName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'kingdomid', 'kingdomid__kingdomName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Kingdom'
                    taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Kingdom', inplace=True)
                    name = Kingdom.objects.filter(Q(**{'kingdomid': value})).values('kingdomid', 'kingdomName')
                    mergeDF['taxa_id'].fillna(name[0]['kingdomid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['kingdomName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Phyla':
                    field = 'phylaid'
                    qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Phyla'
                    taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Phyla', inplace=True)
                    name = Phyla.objects.filter(Q(**{'phylaid': value})).values('phylaid', 'phylaName')
                    mergeDF['taxa_id'].fillna(name[0]['phylaid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['phylaName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Class':
                    field = 'classid'
                    qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'classid', 'classid__className', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Class'
                    taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Class', inplace=True)
                    name = Class.objects.filter(Q(**{'classid': value})).values('classid', 'className')
                    mergeDF['taxa_id'].fillna(name[0]['classid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['className'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Order':
                    field = 'orderid'
                    qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Order'
                    taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Order', inplace=True)
                    name = Order.objects.filter(Q(**{'orderid': value})).values('orderid', 'orderName')
                    mergeDF['taxa_id'].fillna(name[0]['orderid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['orderName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Family':
                    field = 'familyid'
                    qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Famiily'
                    taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Family', inplace=True)
                    name = Family.objects.filter(Q(**{'familyid': value})).values('familyid', 'familyName')
                    mergeDF['taxa_id'].fillna(name[0]['familyid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['familyName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Genus':
                    field = 'genusid'
                    qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Genus'
                    taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Genus', inplace=True)
                    name = Genus.objects.filter(Q(**{'genusid': value})).values('genusid', 'genusName')
                    mergeDF['taxa_id'].fillna(name[0]['genusid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['genusName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

                elif key == 'Species':
                    field = 'speciesid'
                    qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values()
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Species'
                    taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Species', inplace=True)
                    name = Kingdom.objects.filter(Q(**{'speciesid': value})).values('speciesid', 'speciesName')
                    mergeDF['taxa_id'].fillna(name[0]['speciesid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['speciesName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

            elif type(value) is list:
                if key == 'Kingdom':
                    for item in value:
                        field = 'kingdomid'
                        qs1 = ProfileKingdom.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'kingdomid', 'kingdomid__kingdomName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'kingdomid', 'kingdomid__kingdomName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Kingdom'
                        taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Kingdom', inplace=True)
                        name = Kingdom.objects.filter(Q(**{'kingdomid': item})).values('kingdomid', 'kingdomName')
                        mergeDF['taxa_id'].fillna(name[0]['kingdomid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['kingdomName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Phyla':
                    for item in value:
                        field = 'phylaid'
                        qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Phyla'
                        taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Phyla', inplace=True)
                        name = Phyla.objects.filter(Q(**{'phylaid': item})).values('phylaid', 'phylaName')
                        mergeDF['taxa_id'].fillna(name[0]['phylaid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['phylaName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Class':
                    for item in value:
                        field = 'classid'
                        qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'classid', 'classid__className', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Class'
                        taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Class', inplace=True)
                        name = Class.objects.filter(Q(**{'classid': item})).values('classid', 'className')
                        mergeDF['taxa_id'].fillna(name[0]['classid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['className'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Order':
                    for item in value:
                        field = 'orderid'
                        qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Order'
                        taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Order', inplace=True)
                        name = Order.objects.filter(Q(**{'orderid': item})).values('orderid', 'orderName')
                        mergeDF['taxa_id'].fillna(name[0]['orderid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['orderName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Family':
                    for item in value:
                        field = 'familyid'
                        qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Family'
                        taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Family', inplace=True)
                        name = Family.objects.filter(Q(**{'familyid': item})).values('familyid', 'familyName')
                        mergeDF['taxa_id'].fillna(name[0]['familyid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['familyName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Genus':
                    for item in value:
                        field = 'genusid'
                        qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Genus'
                        taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Genus', inplace=True)
                        name = Genus.objects.filter(Q(**{'genusid': item})).values('genusid', 'genusName')
                        mergeDF['taxa_id'].fillna(name[0]['genusid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['genusName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

                elif key == 'Species':
                    for item in value:
                        field = 'speciesid'
                        qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich')
                        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich'])
                        taxaDF['taxa'] = 'Species'
                        taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                        mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                        mergeDF['rel_abund'].fillna(0, inplace=True)
                        mergeDF['rich'].fillna(0, inplace=True)
                        mergeDF['taxa'].fillna('Species', inplace=True)
                        name = Species.objects.filter(Q(**{'speciesid': item})).values('speciesid', 'speciesName')
                        mergeDF['taxa_id'].fillna(name[0]['speciesid'], inplace=True)
                        mergeDF['taxa_name'].fillna(name[0]['speciesName'], inplace=True)
                        if finalDF.empty:
                            finalDF = mergeDF
                        else:
                            finalDF = finalDF.append(mergeDF)

        # Set datatypes
        finalDF[['x-value', 'rich', 'rel_abund']] = finalDF[['x-value', 'rich', 'rel_abund']].astype(float)

        finalDict = {'abund': [], 'rich': []}
        abundList = []
        richList = []
        grouped = finalDF.groupby(['taxa_id', 'taxa', 'taxa_name'])

        for name, group in grouped:
            abund_slope, abund_intercept, abund_r_value, abund_p_value, abund_std_err = linregress(group['x-value'], group['rel_abund'])
            abund_pred = abund_intercept + abund_slope * group['x-value']
            abund_r_sq = abund_r_value * abund_r_value
            rich_slope, rich_intercept, rich_r_value, rich_p_value, rich_std_err = linregress(group['x-value'], group['rich'])
            rich_pred = rich_intercept + rich_slope * group['x-value']
            rich_r_sq = rich_r_value * rich_r_value
            group['abund_pred'] = abund_pred
            group['abund_r_sq'] = abund_r_sq
            group['rich_pred'] = rich_pred
            group['rich_r_sq'] = rich_r_sq
            abundSeriesDict = {}
            abundValuesList = []
            richSeriesDict = {}
            richValuesList = []

            for index, row in group.iterrows():
                abundValueDict = {}
                richValueDict = {}

                abundValueDict['x'] = row['x-value']
                abundValueDict['y_abund'] = row['rel_abund']
                abundValueDict['pred_y_abund'] = row['abund_pred']
                abundValuesList.append(abundValueDict)

                richValueDict['x'] = row['x-value']
                richValueDict['y_rich'] = row['rich']
                richValueDict['pred_y_rich'] = row['rich_pred']
                richValuesList.append(richValueDict)

            abundSeriesDict['key'] = name[1] + ": " + name[2]
            abundSeriesDict['r_square'] = abund_r_sq
            abundSeriesDict['p_value'] = abund_p_value
            abundSeriesDict['std_err'] = abund_std_err
            abundSeriesDict['slope'] = abund_slope
            abundSeriesDict['intercept'] = abund_intercept
            abundSeriesDict['values'] = abundValuesList

            richSeriesDict['key'] = name[1] + ": " + name[2]
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


