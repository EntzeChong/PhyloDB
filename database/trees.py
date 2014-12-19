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
from utils import multidict, catDataFrame, quantDataFrame
from scipy import stats
from numpy import *
from pyvttbl import Anova, Anova1way, DataFrame
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


def getCatGraphData(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    qs1 = Sample.objects.all().filter(sampleid__in=selected)

    if request.is_ajax():
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        taxaString = all["taxa"]
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        finalDF = catDataFrame(qs1, taxaDict, metaDict)

        final_fieldList = []
        for key in metaDict:
            final_fieldList.append(key)

        finalDict = {}
        seriesList_abund = []
        seriesList_rich = []
        xAxisDict = {}
        yAxisDict_abund = {}
        yAxisDict_rich = {}
        grouped1 = finalDF.groupby(['rank', 'taxa', 'taxa_name', 'taxa_id'])
        for name1, group1 in grouped1:
            categoryList = []
            dataList_abund = []
            dataList_rich = []
            groupedList = []
            for field in final_fieldList:
                grouped2 = group1.groupby(field).mean()
                categoryDict = {}
                categoryDict['name'] = field
                categoryDict['categories'] = list(grouped2.index.T)
                categoryList.append(categoryDict)
                dataList_abund.extend(list(grouped2['rel_abund'].T))
                dataList_rich.extend(list(grouped2['rich'].T))
                groupedDict = {}
                groupedDict['rotation'] = 0
                groupedList.append(groupedDict)

            seriesDict_abund = {}
            seriesDict_abund['name'] = name1[1] + ": " + name1[2]
            seriesDict_abund['data'] = dataList_abund
            seriesList_abund.append(seriesDict_abund)

            seriesDict_rich = {}
            seriesDict_rich['name'] = name1[1] + ": " + name1[2]
            seriesDict_rich['data'] = dataList_rich
            seriesList_rich.append(seriesDict_rich)

            xTitle = {}
            xTitle['text'] = ''
            labelDict = {}
            labelDict['groupedOptions'] = groupedList
            labelDict['rotation'] = 0     # this is for the 1st axis
            xAxisDict['title'] = xTitle
            xAxisDict['categories'] = categoryList
            xAxisDict['labels'] = labelDict

            yTitle_abund = {}
            yTitle_abund['text'] = 'Relative Abundance'
            yAxisDict_abund['title'] = yTitle_abund

            yTitle_rich = {}
            yTitle_rich['text'] = 'OTU Richness'
            yAxisDict_rich['title'] = yTitle_rich

        finalDict['series_abund'] = seriesList_abund
        finalDict['series_rich'] = seriesList_rich
        finalDict['xAxis'] = xAxisDict
        finalDict['yAxis_abund'] = yAxisDict_abund
        finalDict['yAxis_rich'] = yAxisDict_rich

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')


def ANOVA(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')
    qs1 = Sample.objects.all().filter(sampleid__in=selected)

    if request.is_ajax():
        button = request.GET["button"]
        allJson = request.GET["all"]
        all = simplejson.loads(allJson)

        taxaString = all["taxa"]
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        finalDF = catDataFrame(qs1, taxaDict, metaDict)

        final_fieldList = []
        for key in metaDict:
            final_fieldList.append(key)

        result = ""
        grouped1 = finalDF.groupby(['rank', 'taxa', 'taxa_name', 'taxa_id'])
        for name1, group1 in grouped1:
            for field in final_fieldList:
                trtList = []
                valList = []
                grouped2 = pd.DataFrame()
                if button == '1':
                    grouped2 = group1.groupby(field)['rel_abund']
                elif button == '2':
                    grouped2 = group1.groupby(field)['rich']
                for name, group in grouped2:
                    trtList.append(name)
                    valList.append(list(group.T))

                try:
                    D = Anova1way()
                    D.run(valList, conditions_list=trtList)
                    result = result + '===============================================\n'
                    result = result + 'Taxa level: ' + str(name1[1]) + '\n'
                    result = result + 'Taxa name: ' + str(name1[2]) + '\n'
                    if button == '1':
                        result = result + 'Dependent Variable: Relative abundance' + '\n'
                    elif button == '2':
                        result = result + 'Dependent Variable: OTU Richness' + '\n'
                    result = result + 'Independent Variable: ' + str(field) + '\n'
                    result = result + str(D) + '\n'
                    result = result + '===============================================\n'
                    result = result + '\n\n\n\n'
                except:
                    result = result + '===============================================\n'
                    result = result + 'Taxa level: ' + str(name1[1]) + '\n'
                    result = result + 'Taxa name: ' + str(name1[2]) + '\n'
                    if button == '1':
                        result = result + 'Dependent Variable: Relative abundance' + '\n'
                    elif button == '2':
                        result = result + 'Dependent Variable: OTU Richness' + '\n'
                    result = result + 'Independent Variable: ' + str(field) + '\n'
                    result = result + 'ANOVA cannot be performed...\n'
                    result = result + '===============================================\n'
                    result = result + '\n\n\n\n'

        return HttpResponse(result, content_type='application/text')


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

        finalDF = quantDataFrame(qs1, taxaDict, metaDict)

        final_fieldList = []
        for key, value in metaDict.items():
            final_fieldList.append(value)

        finalDict = {}
        seriesList_abund = []
        seriesList_rich = []
        xAxisDict = {}
        yAxisDict_rich = {}
        yAxisDict_abund = {}
        grouped1 = finalDF.groupby(['rank', 'taxa', 'taxa_name', 'taxa_id'])
        for name1, group1 in grouped1:
            dataList_abund = group1[['x-value', 'rel_abund']].values.tolist()
            dataList_rich = group1[['x-value', 'rich']].values.tolist()

            seriesDict_abund = {}
            seriesDict_abund['regression'] = 'true'
            regDict = {}
            regDict['type'] = 'linear'
            regDict['label'] = 'R2 = %r2<br>%eq'
            seriesDict_abund['regressionSettings'] = regDict
            seriesDict_abund['name'] = name1[1] + ": " + name1[2]
            seriesDict_abund['data'] = dataList_abund
            seriesList_abund.append(seriesDict_abund)

            seriesDict_rich = {}
            seriesDict_rich['regression'] = 'true'
            regDict = {}
            regDict['type'] = 'linear'
            regDict['label'] = 'R2 = %r2<br>%eq'
            seriesDict_rich['regressionSettings'] = regDict
            seriesDict_rich['name'] = name1[1] + ": " + name1[2]
            seriesDict_rich['data'] = dataList_rich
            seriesList_rich.append(seriesDict_rich)

            xTitle = {}
            xTitle['text'] = final_fieldList[0]
            xAxisDict['title'] = xTitle

            yTitle_abund = {}
            yTitle_abund['text'] = 'Relative Abundance'
            yAxisDict_abund['title'] = yTitle_abund


            yTitle_rich = {}
            yTitle_rich['text'] = 'OTU Richness'
            yAxisDict_rich['title'] = yTitle_rich

        finalDict['series_abund'] = seriesList_abund
        finalDict['series_rich'] = seriesList_rich
        finalDict['xAxis'] = xAxisDict
        finalDict['yAxis_abund'] = yAxisDict_abund
        finalDict['yAxis_rich'] = yAxisDict_rich

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')
