import collections
import pickle
import operator
import simplejson
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q
from models import Project, Sample, Collect, Soil_class, Management, User
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile
from models import ProfileKingdom, ProfilePhyla, ProfileClass, ProfileOrder, ProfileFamily, ProfileGenus, ProfileSpecies
from utils import multidict, catAlphaDF, quantAlphaDF, alphaTaxaDF, catBetaMetaDF, quantBetaMetaDF, betaTaxaDF
from utils import permanova_oneway, PCoA
import pandas as pd
import numpy as np
from numpy import *
from pyvttbl import Anova1way
from scipy.spatial.distance import *


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
    myTree = {'title': 'root', 'id': 'root', 'tooltip': 'root', 'isFolder': False,  'hideCheckbox': True, 'expand': True, 'children': []}
    mimark = {'title': 'MIMARKs', 'id': 'mimark', 'tooltip': 'Category', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    collect = {'title': 'Sample Collection', 'id': 'collect', 'tooltip': 'Category', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    soil_class = {'title': 'Soil Classification', 'id': 'soil_class', 'tooltip': 'Category', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    management = {'title': 'Management', 'id': 'management', 'tooltip': 'Category', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    user = {'title': 'User-defined', 'id': 'user', 'tooltip': 'Category', 'isFolder': True,  'hideCheckbox': True, 'children': []}

    list = ['sample_name', 'organism', 'seq_method', 'biome', 'feature', 'geo_loc', 'material']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': 'Field', 'isLazy': True, 'children': []}
        mimark['children'].append(myNode)

    list = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': 'Field', 'isLazy': True, 'children': []}
        collect['children'].append(myNode)

    list = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': 'Field', 'isLazy': True, 'children': []}
        soil_class['children'].append(myNode)

    list = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': 'Field', 'isLazy': True, 'children': []}
        management['children'].append(myNode)

    list = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']
    for i in range(len(list)):
        myNode = {'title': list[i], 'isFolder': True, 'tooltip': 'Field', 'isLazy': True, 'children': []}
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
        field = request.GET["field"]
        mimark = ['sample_name', 'organism', 'seq_method', 'biome', 'feature', 'geo_loc', 'material']
        collect = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
        soil_class = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
        management = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
        user = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']

        myNode = []
        if field in mimark:
            values = Sample.objects.values_list(field, flat='True').filter(sampleid__in=selected).distinct()
            for j in range(len(values)):
                myNode1 = {
                    'title': values[j],
                    'id': field,
                    'tooltip': 'Value',
                    'isFolder': True,
                    'children': []
                }
                args_list = []
                args_list.append(Q(**{field: values[j]}))
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).order_by('sample_name')
                for item in items:
                    myNode2 = {
                        'title': 'Sample: ' + item.sample_name,
                        'id': item.sampleid,
                        'tooltip': 'Project: ' + item.projectid.project_name,
                        'hideCheckbox': True,
                        'isFolder': False
                    }
                    myNode1['children'].append(myNode2)
                myNode.append(myNode1)

        elif field in collect:
            table_field = 'collect__' + field
            values = Sample.objects.values_list(table_field, flat='True').filter(sampleid__in=selected).distinct()
            for j in range(len(values)):
                myNode1 = {
                    'title': values[j],
                    'id': field,
                    'tooltip': 'Value',
                    'isFolder': True,
                    'children': []
                }
                args_list = []
                args_list.append(Q(**{table_field: values[j]}))
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).order_by('sample_name')
                for item in items:
                    myNode2 = {
                        'title': 'Sample: ' + item.sample_name,
                        'id': item.sampleid,
                        'tooltip': 'Project: ' + item.projectid.project_name,
                        'hideCheckbox': True,
                        'isFolder': False
                    }
                    myNode1['children'].append(myNode2)
                myNode.append(myNode1)

        elif field in soil_class:
            table_field = 'soil_class__' + field
            values = Sample.objects.values_list(table_field, flat='True').filter(sampleid__in=selected).distinct()
            for j in range(len(values)):
                myNode1 = {
                    'title': values[j],
                    'id': field,
                    'tooltip': 'Value',
                    'isFolder': True,
                    'children': []
                }
                args_list = []
                args_list.append(Q(**{table_field: values[j]}))
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).order_by('sample_name')
                for item in items:
                    myNode2 = {
                        'title': 'Sample: ' + item.sample_name,
                        'id': item.sampleid,
                        'tooltip': 'Project: ' + item.projectid.project_name,
                        'hideCheckbox': True,
                        'isFolder': False
                    }
                    myNode1['children'].append(myNode2)
                myNode.append(myNode1)

        elif field in management:
            table_field = 'management__' + field
            values = Sample.objects.values_list(table_field, flat='True').filter(sampleid__in=selected).distinct()
            for j in range(len(values)):
                myNode1 = {
                    'title': values[j],
                    'id': field,
                    'tooltip': 'Value',
                    'isFolder': True,
                    'children': []
                }
                args_list = []
                args_list.append(Q(**{table_field: values[j]}))
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).order_by('sample_name')
                for item in items:
                    myNode2 = {
                        'title': 'Sample: ' + item.sample_name,
                        'id': item.sampleid,
                        'tooltip': 'Project: ' + item.projectid.project_name,
                        'hideCheckbox': True,
                        'isFolder': False
                    }
                    myNode1['children'].append(myNode2)
                myNode.append(myNode1)


        elif field in user:
            table_field = 'user__' + field
            values = Sample.objects.values_list(table_field, flat='True').filter(sampleid__in=selected).distinct()
            for j in range(len(values)):
                myNode1 = {
                    'title': values[j],
                    'id': field,
                    'tooltip': 'Value',
                    'isFolder': True,
                    'children': []
                }
                args_list = []
                args_list.append(Q(**{table_field: values[j]}))
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).order_by('sample_name')
                for item in items:
                    myNode2 = {
                        'title': 'Sample: ' + item.sample_name,
                        'id': item.sampleid,
                        'tooltip': 'Project: ' + item.projectid.project_name,
                        'hideCheckbox': True,
                        'isFolder': False
                    }
                    myNode1['children'].append(myNode2)
                myNode.append(myNode1)

        res = simplejson.dumps(myNode, encoding="Latin-1")
        return StreamingHttpResponse(res, content_type='application/json')


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

    list = ['collection_date', 'lat_lon', 'elevation']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'mimark', 'isFolder': False}
        mimark['children'].append(myNode)

    list = ['samp_size', 'samp_weight_dna_ext']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'collect', 'isFolder': False}
        collect['children'].append(myNode)

    list = ['annual_season_precpt', 'annual_season_temp']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'climate', 'isFolder': False}
        climate['children'].append(myNode)

    list = ['bulk_density', 'porosity', 'slope_gradient', 'water_content_soil']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'soil_class', 'isFolder': False}
        soil_class['children'].append(myNode)

    list = ['pH', 'EC', 'tot_C', 'tot_OM', 'tot_N', 'NO3_N', 'NH4_N', 'P', 'K', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'Ca', 'Mg', 'Na', 'B']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'soil_nutrient', 'isFolder': False}
        soil_nutrient['children'].append(myNode)

    list = ['rRNA_copies', 'microbial_biomass_C', 'microbial_biomass_N', 'microbial_respiration']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'microbial', 'isFolder': False}
        microbial['children'].append(myNode)

    list = ['usr_quant1', 'usr_quant2', 'usr_quant3', 'usr_quant4', 'usr_quant5', 'usr_quant6']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'user', 'isFolder': False}
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


def getCatAlphaData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    qs1 = Sample.objects.all().filter(sampleid__in=selected)

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        button = int(all["button"])

        taxaString = all["taxa"]
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        metaDF = catAlphaDF(qs1, metaDict)
        finalDF = alphaTaxaDF(metaDF, taxaDict)

        final_fieldList = []
        for key in metaDict:
            final_fieldList.append(key)

        finalDict = {}
        seriesList = []
        xAxisDict = {}
        yAxisDict = {}
        grouped1 = finalDF.groupby(['rank', 'taxa', 'taxa_name', 'taxa_id'])
        for name1, group1 in grouped1:
            categoryList = []
            dataList = []
            groupedList = []
            for field in final_fieldList:
                grouped2 = group1.groupby(field).mean()
                categoryDict = {}
                categoryDict['name'] = field
                categoryDict['categories'] = list(grouped2.index.T)
                categoryList.append(categoryDict)
                if button == 1:
                    dataList.extend(list(grouped2['count'].T))
                elif button == 2:
                    dataList.extend(list(grouped2['rel_abund'].T))
                elif button == 3:
                    dataList.extend(list(grouped2['rich'].T))
                elif button == 4:
                    dataList.extend(list(grouped2['diversity'].T))
                groupedDict = {}
                groupedDict['rotation'] = 0
                groupedList.append(groupedDict)

            seriesDict = {}
            seriesDict['name'] = name1[1] + ": " + name1[2]
            seriesDict['data'] = dataList
            seriesList.append(seriesDict)

            xTitle = {}
            xTitle['text'] = ''
            labelDict = {}
            labelDict['groupedOptions'] = groupedList
            labelDict['rotation'] = 0
            xAxisDict['title'] = xTitle
            xAxisDict['categories'] = categoryList
            xAxisDict['labels'] = labelDict

            yTitle = {}
            if button == 1:
                yTitle['text'] = 'Sequence Reads'
            elif button == 2:
                yTitle['text'] = 'Relative Abundance'
            elif button == 3:
                yTitle['text'] = 'Species Richness'
            elif button == 4:
                yTitle['text'] = 'Shannon Diversity'
            yAxisDict['title'] = yTitle

        finalDict['series'] = seriesList
        finalDict['xAxis'] = xAxisDict
        finalDict['yAxis'] = yAxisDict

        result = ""
        grouped1 = finalDF.groupby(['rank', 'taxa', 'taxa_name', 'taxa_id'])
        for name1, group1 in grouped1:
            for field in final_fieldList:
                trtList = []
                valList = []
                grouped2 = pd.DataFrame()
                if button == 1:
                    grouped2 = group1.groupby(field)['count']
                elif button == 2:
                    grouped2 = group1.groupby(field)['rel_abund']
                elif button == 3:
                    grouped2 = group1.groupby(field)['rich']
                elif button == 4:
                    grouped2 = group1.groupby(field)['diversity']
                for name, group in grouped2:
                    trtList.append(name)
                    valList.append(list(group.T))

                try:
                    D = Anova1way()
                    D.run(valList, conditions_list=trtList)
                    result = result + '===============================================\n'
                    result = result + 'Taxa level: ' + str(name1[1]) + '\n'
                    result = result + 'Taxa name: ' + str(name1[2]) + '\n'
                    if button == 1:
                        result = result + 'Dependent Variable: Sequence Reads' + '\n'
                    elif button == 2:
                        result = result + 'Dependent Variable: Relative Abundance' + '\n'
                    elif button == 3:
                        result = result + 'Dependent Variable: Species Richness' + '\n'
                    elif button == 4:
                        result = result + 'Dependent Variable: Shannon Diversity' + '\n'
                    result = result + 'Independent Variable: ' + str(field) + '\n'
                    result = result + str(D) + '\n'
                    result = result + '===============================================\n'
                    result = result + '\n\n\n\n'
                except:
                    result = result + '===============================================\n'
                    result = result + 'Taxa level: ' + str(name1[1]) + '\n'
                    result = result + 'Taxa name: ' + str(name1[2]) + '\n'
                    if button == 1:
                        result = result + 'Dependent Variable: Sequence Reads' + '\n'
                    elif button == 2:
                        result = result + 'Dependent Variable: Relative Abundance' + '\n'
                    elif button == 3:
                        result = result + 'Dependent Variable: Species Richness' + '\n'
                    elif button == 4:
                        result = result + 'Dependent Variable: Shannon Diversity' + '\n'
                    result = result + 'Independent Variable: ' + str(field) + '\n'
                    result = result + 'ANOVA cannot be performed...\n'
                    result = result + '===============================================\n'
                    result = result + '\n\n\n\n'

        finalDict['text'] = result

        res = simplejson.dumps(finalDict)

        return HttpResponse(res, content_type='application/json')


def getQuantAlphaData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    qs1 = Sample.objects.all().filter(sampleid__in=selected)

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        button = int(all["button"])
        regType = int(all["regType"])

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        taxaString = all["taxa"]
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        metaDF = quantAlphaDF(qs1, metaDict)

        finalDF = alphaTaxaDF(metaDF, taxaDict)
        finalDF['x-value'] = finalDF['x-value'].astype(float)

        final_fieldList = []
        for key, value in metaDict.items():
            final_fieldList.append(value)

        finalDict = {}
        seriesList = []
        xAxisDict = {}
        yAxisDict = {}
        grouped1 = finalDF.groupby(['rank', 'taxa', 'taxa_name', 'taxa_id'])
        for name1, group1 in grouped1:
            dataList = []
            if button == 1:
                dataList = group1[['x-value', 'count']].values.tolist()
            elif button == 2:
                dataList = group1[['x-value', 'rel_abund']].values.tolist()
            elif button == 3:
                dataList = group1[['x-value', 'rich']].values.tolist()
            elif button == 4:
                dataList = group1[['x-value', 'diversity']].values.tolist()

            seriesDict = {}
            seriesDict['regression'] = 'true'
            regDict = {}
            if regType == 1:
                regDict['type'] = 'linear'
            elif regType == 2:
                regDict['type'] = 'polynomial'
            elif regType == 3:
                regDict['type'] = 'exponential'
            elif regType == 4:
                regDict['type'] = 'logarithmic'
            elif regType == 5:
                regDict['type'] = 'power'

            seriesDict['regressionSettings'] = regDict
            seriesDict['name'] = name1[1] + ": " + name1[2]
            seriesDict['data'] = dataList
            seriesList.append(seriesDict)

            xTitle = {}
            xTitle['text'] = final_fieldList[0]
            xAxisDict['title'] = xTitle

            yTitle = {}
            if button == 1:
                yTitle['text'] = 'Sequence Reads'
            elif button == 2:
                yTitle['text'] = 'Relative Abundance'
            elif button == 3:
                yTitle['text'] = 'Species Richness'
            elif button == 4:
                yTitle['text'] = 'Shannon Diversity'
            yAxisDict['title'] = yTitle

        finalDict['series'] = seriesList
        finalDict['xAxis'] = xAxisDict
        finalDict['yAxis'] = yAxisDict

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')


def getCatBetaData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    qs1 = Sample.objects.all().filter(sampleid__in=selected)

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        button = int(all["button"])
        taxaLevel = int(all["taxa"])
        distance = int(all["distance"])
        PC1 = all["PC1"]
        PC2 = all["PC2"]

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        fieldList = []
        for key in metaDict:
            fieldList.append(key)

        metaDF = catBetaMetaDF(qs1, metaDict)
        myset = list(metaDF['sampleid'].T)

        taxaDF = betaTaxaDF(metaDF, myset, taxaLevel)

        sampleList = list(set(metaDF['sampleid'].tolist()))

        taxaDF2 = pd.DataFrame()
        if button == 1:
            fieldList.extend(['rel_abund', 'rich', 'diversity'])
            taxaDF2 = taxaDF.drop(fieldList, axis=1)
            taxaDF2.rename(columns={'count': 'response'}, inplace=True)
        elif button == 2:
            fieldList.extend(['count', 'rich', 'diversity'])
            taxaDF2 = taxaDF.drop(fieldList, axis=1)
            taxaDF2.rename(columns={'rel_abund': 'response'}, inplace=True)
        elif button == 3:
            fieldList.extend(['count', 'rel_abund', 'diversity'])
            taxaDF2 = taxaDF.drop(fieldList, axis=1)
            taxaDF2.rename(columns={'rich': 'response'}, inplace=True)
        elif button == 4:
            fieldList.extend(['count', 'rel_abund', 'rich'])
            taxaDF2 = taxaDF.drop(fieldList, axis=1)
            taxaDF2.rename(columns={'diversity': 'response'}, inplace=True)

        taxaDF2.set_index(['taxaid', 'sampleid'], drop=True, inplace=True)

        taxaFinalDF = pd.DataFrame()
        for sample in sampleList:
            df = taxaDF2.iloc[taxaDF2.index.get_level_values('sampleid') == sample]
            df.reset_index(inplace=True)
            df2 = df.drop('sampleid', axis=1)
            if taxaFinalDF.empty:
                taxaFinalDF = df2
                taxaFinalDF.rename(columns={'response': sample}, inplace=True)
            else:
                taxaFinalDF = taxaFinalDF.merge(df2, on='taxaid', how='outer')
                taxaFinalDF.reset_index(drop=True, inplace=True)
                taxaFinalDF.rename(columns={'response': sample}, inplace=True)
                taxaFinalDF.fillna(0, inplace=True)
        taxaFinalDF.set_index('taxaid', drop=True, inplace=True)

        taxa = taxaFinalDF.reset_index(drop=True).T
        metaDF.set_index('sampleid', drop=True, inplace=True)
        finalDF = taxa.join(metaDF)

        fieldList = []
        for key in metaDict:
            fieldList.append(key)

        pcoaDF = finalDF.reset_index(drop=True)
        matrixDF = pcoaDF.drop(fieldList, axis=1)

        datamtx = asarray(matrixDF)
        numrows, numcols = shape(datamtx)
        dists = zeros((numrows, numrows))

        if distance == 1:
            dist = pdist(datamtx, 'braycurtis')
            dists = squareform(dist)
        elif distance == 2:
            dist = pdist(datamtx, 'canberra')
            dists = squareform(dist)
        elif distance == 3:
            dist = pdist(datamtx, 'dice')
            dists = squareform(dist)
        elif distance == 4:
            dist = pdist(datamtx, 'euclidean')
            dists = squareform(dist)
        elif distance == 5:
            dist = pdist(datamtx, 'jaccard')
            dists = squareform(dist)

        eigvals, coordinates, proportion_explained = PCoA(dists)

        numaxes = len(eigvals)
        axesList = []
        for i in range(numaxes):
            j = i + 1
            axesList.append('PC' + str(j))

        valsDF = pd.DataFrame(eigvals, columns=['EigenVals'], index=axesList)
        propDF = pd.DataFrame(proportion_explained, columns=['Variance Explained (R2)'], index=axesList)
        eigenDF = valsDF.join(propDF)

        pcoaDF = pd.DataFrame(coordinates, columns=axesList, index=sampleList)
        resultDF = metaDF.join(pcoaDF)
        pd.set_option('display.max_rows', resultDF.shape[0], 'display.max_columns', resultDF.shape[1], 'display.width', 1000)

        trtList = list(finalDF[fieldList[0]].T)
        bigf, p = permanova_oneway(dists, trtList, 200)

        finalDict = {}
        seriesList = []
        xAxisDict = {}
        yAxisDict = {}
        for field in fieldList:
            grouped = resultDF.groupby(field)
            for name, group in grouped:
                dataList = group[[PC1, PC2]].values.tolist()

                seriesDict = {}
                seriesDict['name'] = field + ": " + name
                seriesDict['data'] = dataList
                seriesList.append(seriesDict)

        xTitle = {}
        xTitle['text'] = PC1
        xAxisDict['title'] = xTitle

        yTitle = {}
        yTitle['text'] = PC2
        yAxisDict['title'] = yTitle

        finalDict['series'] = seriesList
        finalDict['xAxis'] = xAxisDict
        finalDict['yAxis'] = yAxisDict

        result = ""
        result = result + '===============================================\n'
        if taxaLevel == 1:
            result = result + 'Taxa level: Kingdom' + '\n'
        elif taxaLevel == 2:
            result = result + 'Taxa level: Phyla' + '\n'
        elif taxaLevel == 3:
            result = result + 'Taxa level: Class' + '\n'
        elif taxaLevel == 4:
            result = result + 'Taxa level: Order' + '\n'
        elif taxaLevel == 5:
            result = result + 'Taxa level: Family' + '\n'
        elif taxaLevel == 6:
            result = result + 'Taxa level: Genus' + '\n'
        elif taxaLevel == 7:
            result = result + 'Taxa level: Species' + '\n'

        if button == 1:
            result = result + 'Dependent Variable: Sequence Reads' + '\n'
        elif button == 2:
            result = result + 'Dependent Variable: Relative Abundance' + '\n'
        elif button == 3:
            result = result + 'Dependent Variable: Species Richness' + '\n'
        elif button == 4:
            result = result + 'Dependent Variable: Shannon Diversity' + '\n'

        result = result + 'Independent Variable: ' + str(fieldList[0]) + '\n'

        if distance == 1:
            result = result + 'Distance score: Bray-Curtis' + '\n'
        elif distance == 2:
            result = result + 'Distance score: Canberra' + '\n'
        elif distance == 3:
            result = result + 'Distance score: Dice' + '\n'
        elif distance == 4:
            result = result + 'Distance score: Euclidean' + '\n'
        elif distance == 5:
            result = result + 'Distance score: Jaccard' + '\n'

        result = result + '===============================================\n'
        result = result + 'perMANOVA results' + '\n'
        result = result + 'f-value: ' + str(bigf) + '\n'
        result = result + 'p-value: ' + str(p) + '\n'
        result = result + '===============================================\n'
        result = result + str(eigenDF) + '\n'
        result = result + '===============================================\n'

        result = result + str(resultDF) + '\n'
        result = result + '\n\n\n\n'

        finalDict['text'] = result

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')


def getQuantBetaData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    qs1 = Sample.objects.all().filter(sampleid__in=selected)

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        button = int(all["button"])
        taxaLevel = int(all["taxa"])
        distance = int(all["distance"])
        PC1 = all["PC1"]
        PC2 = all["PC2"]

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        fieldList = []
        for key, value in metaDict.items():
            fieldList.append(value)

        metaDF = quantBetaMetaDF(qs1, metaDict)
        myset = list(metaDF['sampleid'].T)

        taxaDF = betaTaxaDF(metaDF, myset, taxaLevel)

        sampleList = list(set(metaDF['sampleid'].tolist()))

        taxaDF2 = pd.DataFrame()
        if button == 1:
            fieldList.extend(['rel_abund', 'rich', 'diversity'])
            taxaDF2 = taxaDF.drop(fieldList, axis=1)
            taxaDF2.rename(columns={'count': 'response'}, inplace=True)
        elif button == 2:
            fieldList.extend(['count', 'rich', 'diversity'])
            taxaDF2 = taxaDF.drop(fieldList, axis=1)
            taxaDF2.rename(columns={'rel_abund': 'response'}, inplace=True)
        elif button == 3:
            fieldList.extend(['count', 'rel_abund', 'diversity'])
            taxaDF2 = taxaDF.drop(fieldList, axis=1)
            taxaDF2.rename(columns={'rich': 'response'}, inplace=True)
        elif button == 4:
            fieldList.extend(['count', 'rel_abund', 'rich'])
            taxaDF2 = taxaDF.drop(fieldList, axis=1)
            taxaDF2.rename(columns={'diversity': 'response'}, inplace=True)

        taxaDF2.set_index(['taxaid', 'sampleid'], drop=True, inplace=True)

        taxaFinalDF = pd.DataFrame()
        for sample in sampleList:
            df = taxaDF2.iloc[taxaDF2.index.get_level_values('sampleid') == sample]
            df.reset_index(inplace=True)
            df2 = df.drop('sampleid', axis=1)
            if taxaFinalDF.empty:
                taxaFinalDF = df2
                taxaFinalDF.rename(columns={'response': sample}, inplace=True)
            else:
                taxaFinalDF = taxaFinalDF.merge(df2, on='taxaid', how='outer')
                taxaFinalDF.reset_index(drop=True, inplace=True)
                taxaFinalDF.rename(columns={'response': sample}, inplace=True)
                taxaFinalDF.fillna(0, inplace=True)
        taxaFinalDF.set_index('taxaid', drop=True, inplace=True)

        taxa = taxaFinalDF.reset_index(drop=True).T
        metaDF.set_index('sampleid', drop=True, inplace=True)
        finalDF = taxa.join(metaDF)
        fieldList = []
        for key, value in metaDict.items():
            fieldList.append(value)

        pcoaDF = finalDF.reset_index(drop=True)
        matrixDF = pcoaDF.drop(fieldList, axis=1)

        datamtx = asarray(matrixDF)
        numrows, numcols = shape(datamtx)
        dists = zeros((numrows, numrows))

        if distance == 1:
            dist = pdist(datamtx, 'braycurtis')
            dists = squareform(dist)
        elif distance == 2:
            dist = pdist(datamtx, 'canberra')
            dists = squareform(dist)
        elif distance == 3:
            dist = pdist(datamtx, 'dice')
            dists = squareform(dist)
        elif distance == 4:
            dist = pdist(datamtx, 'euclidean')
            dists = squareform(dist)
        elif distance == 5:
            dist = pdist(datamtx, 'jaccard')
            dists = squareform(dist)

        eigvals, coordinates, proportion_explained = PCoA(dists)

        numaxes = len(eigvals)
        axesList = []
        for i in range(numaxes):
            j = i + 1
            axesList.append('PC' + str(j))

        valsDF = pd.DataFrame(eigvals, columns=['EigenVals'], index=axesList)
        propDF = pd.DataFrame(proportion_explained, columns=['Variance Explained (R2)'], index=axesList)
        eigenDF = valsDF.join(propDF)

        pcoaDF = pd.DataFrame(coordinates, columns=axesList, index=sampleList)
        resultDF = metaDF.join(pcoaDF)
        pd.set_option('display.max_rows', resultDF.shape[0], 'display.max_columns', resultDF.shape[1], 'display.width', 1000)

        finalDict = {}
        seriesList = []
        xAxisDict = {}
        yAxisDict = {}
        dataList = resultDF[[PC1, PC2]].values.tolist()

        seriesDict = {}
        seriesDict['name'] = fieldList
        seriesDict['data'] = dataList
        seriesList.append(seriesDict)

        xTitle = {}
        xTitle['text'] = PC1
        xAxisDict['title'] = xTitle

        yTitle = {}
        yTitle['text'] = PC2
        yAxisDict['title'] = yTitle

        finalDict['series'] = seriesList
        finalDict['xAxis'] = xAxisDict
        finalDict['yAxis'] = yAxisDict

        result = ""
        result = result + '===============================================\n'
        if taxaLevel == 1:
            result = result + 'Taxa level: Kingdom' + '\n'
        elif taxaLevel == 2:
            result = result + 'Taxa level: Phyla' + '\n'
        elif taxaLevel == 3:
            result = result + 'Taxa level: Class' + '\n'
        elif taxaLevel == 4:
            result = result + 'Taxa level: Order' + '\n'
        elif taxaLevel == 5:
            result = result + 'Taxa level: Family' + '\n'
        elif taxaLevel == 6:
            result = result + 'Taxa level: Genus' + '\n'
        elif taxaLevel == 7:
            result = result + 'Taxa level: Species' + '\n'

        if button == 1:
            result = result + 'Dependent Variable: Sequence Reads' + '\n'
        elif button == 2:
            result = result + 'Dependent Variable: Relative Abundance' + '\n'
        elif button == 3:
            result = result + 'Dependent Variable: Species Richness' + '\n'
        elif button == 4:
            result = result + 'Dependent Variable: Shannon Diversity' + '\n'

        result = result + 'Independent Variable: ' + str(fieldList[0]) + '\n'

        if distance == 1:
            result = result + 'Distance score: Bray-Curtis' + '\n'
        elif distance == 2:
            result = result + 'Distance score: Canberra' + '\n'
        elif distance == 3:
            result = result + 'Distance score: Dice' + '\n'
        elif distance == 4:
            result = result + 'Distance score: Euclidean' + '\n'
        elif distance == 5:
            result = result + 'Distance score: Jaccard' + '\n'

        result = result + '===============================================\n'
        result = result + str(eigenDF) + '\n'

        result = result + '===============================================\n'
        result = result + str(resultDF) + '\n'
        result = result + '\n\n\n\n'

        finalDict['text'] = result

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')
