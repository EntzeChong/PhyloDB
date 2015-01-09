import collections
import pickle
import operator
import simplejson
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q
from models import Project, Sample
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile
from utils import multidict, catAlphaDF, quantAlphaDF, taxaProfileDF, normalizeAlpha, normalizeBeta, catBetaMetaDF, quantBetaMetaDF
from utils import permanova_oneway, PCoA
import pandas as pd
import numpy as np
from numpy import *
from pyvttbl import Anova1way
from scipy.spatial.distance import *
from scipy import stats


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

    list = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc_country', 'geo_loc_state', 'geo_loc_city', 'geo_loc_farm', 'geo_loc_plot', 'material']
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
        mimark = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc_country', 'geo_loc_state', 'geo_loc_city',  'geo_loc_farm', 'geo_loc_plot', 'material']
        collect = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
        soil_class = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
        management = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
        user = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']

        myNode = []
        if field in mimark:
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            values = Sample.objects.values_list(field, flat='True').filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).distinct()
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
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
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
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            values = Sample.objects.values_list(table_field, flat='True').filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).distinct()
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
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
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
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            values = Sample.objects.values_list(table_field, flat='True').filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).distinct()
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
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
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
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            values = Sample.objects.values_list(table_field, flat='True').filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).distinct()
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
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
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
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            values = Sample.objects.values_list(table_field, flat='True').filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).distinct()
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
                items = Sample.objects.filter(reduce(operator.or_, args_list)).filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
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
    soil_nutrient = {'title': 'Soil pH / Nutrients', 'tooltip': 'Soil Nutrient', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    microbial = {'title': 'Microbial Biomass', 'tooltip': 'Microbial Biomass', 'isFolder': True,  'hideCheckbox': True, 'children': []}
    user = {'title': 'User-defined', 'tooltip': 'User_defined', 'isFolder': True,  'hideCheckbox': True, 'children': []}

    list = ['latitude', 'longitude', 'elevation']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'mimark', 'isFolder': True, 'isLazy': True, 'children': []}
        mimark['children'].append(myNode)

    list = ['samp_size', 'samp_weight_dna_ext']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'collect', 'isFolder': True, 'isLazy': True, 'children': []}
        collect['children'].append(myNode)

    list = ['annual_season_precpt', 'annual_season_temp']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'climate', 'isFolder': True, 'isLazy': True, 'children': []}
        climate['children'].append(myNode)

    list = ['bulk_density', 'porosity', 'slope_gradient', 'water_content_soil']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'soil_class', 'isFolder': True, 'isLazy': True, 'children': []}
        soil_class['children'].append(myNode)

    list = ['pH', 'EC', 'tot_C', 'tot_OM', 'tot_N', 'NO3_N', 'NH4_N', 'P', 'K', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'Ca', 'Mg', 'Na', 'B']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'soil_nutrient', 'isFolder': True, 'isLazy': True, 'children': []}
        soil_nutrient['children'].append(myNode)

    list = ['rRNA_copies', 'microbial_biomass_C', 'microbial_biomass_N', 'microbial_respiration']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'microbial', 'isFolder': True, 'isLazy': True, 'children': []}
        microbial['children'].append(myNode)

    list = ['usr_quant1', 'usr_quant2', 'usr_quant3', 'usr_quant4', 'usr_quant5', 'usr_quant6']
    for i in range(len(list)):
        myNode = {'title': list[i], 'tooltip': 'user', 'isFolder': True, 'isLazy': True, 'children': []}
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


def getSampleQuantTreeChildren(request):
    samples = Sample.objects.all()
    samples.query = pickle.loads(request.session['selected_samples'])
    selected = samples.values_list('sampleid')

    if request.is_ajax():
        field = request.GET["field"]
        mimark = ['latitude', 'longitude', 'elevation']
        collect = ['samp_size', 'samp_weight_dna_ext']
        climate = ['annual_season_precpt', 'annual_season_temp']
        soil_class = ['bulk_density', 'porosity', 'slope_gradient', 'water_content_soil']
        soil_nutrient = ['pH', 'EC', 'tot_C', 'tot_OM', 'tot_N', 'NO3_N', 'NH4_N', 'P', 'K', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'Ca', 'Mg', 'Na', 'B']
        microbial = ['rRNA_copies', 'microbial_biomass_C', 'microbial_biomass_N', 'microbial_respiration']
        user = ['usr_quant1', 'usr_quant2', 'usr_quant3', 'usr_quant4', 'usr_quant5', 'usr_quant6']

        myNode = []
        if field in mimark:
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            items = Sample.objects.filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
            for item in items:
                myNode1 = {
                    'title': 'Sample: ' + item.sample_name,
                    'id': item.sampleid,
                    'tooltip': 'Project: ' + item.projectid.project_name,
                    'hideCheckbox': True,
                    'isFolder': False
                }
                myNode.append(myNode1)

        elif field in collect:
            table_field = 'collect__' + field
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            items = Sample.objects.filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
            for item in items:
                myNode1 = {
                    'title': 'Sample: ' + item.sample_name,
                    'id': item.sampleid,
                    'tooltip': 'Project: ' + item.projectid.project_name,
                    'hideCheckbox': True,
                    'isFolder': False
                }
                myNode.append(myNode1)

        elif field in climate:
            table_field = 'climate__' + field
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            items = Sample.objects.filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
            for item in items:
                myNode1 = {
                    'title': 'Sample: ' + item.sample_name,
                    'id': item.sampleid,
                    'tooltip': 'Project: ' + item.projectid.project_name,
                    'hideCheckbox': True,
                    'isFolder': False
                }
                myNode.append(myNode1)

        elif field in soil_class:
            table_field = 'soil_class__' + field
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            items = Sample.objects.filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
            for item in items:
                myNode1 = {
                    'title': 'Sample: ' + item.sample_name,
                    'id': item.sampleid,
                    'tooltip': 'Project: ' + item.projectid.project_name,
                    'hideCheckbox': True,
                    'isFolder': False
                }
                myNode.append(myNode1)

        elif field in soil_nutrient:
            table_field = 'soil_nutrient__' + field
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            items = Sample.objects.filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
            for item in items:
                myNode1 = {
                    'title': 'Sample: ' + item.sample_name,
                    'id': item.sampleid,
                    'tooltip': 'Project: ' + item.projectid.project_name,
                    'hideCheckbox': True,
                    'isFolder': False
                }
                myNode.append(myNode1)

        elif field in microbial:
            table_field = 'microbial__' + field
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            items = Sample.objects.filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
            for item in items:
                myNode1 = {
                    'title': 'Sample: ' + item.sample_name,
                    'id': item.sampleid,
                    'tooltip': 'Project: ' + item.projectid.project_name,
                    'hideCheckbox': True,
                    'isFolder': False
                }
                myNode.append(myNode1)

        elif field in user:
            table_field = 'user__' + field
            exclude_list = []
            exclude_list.append(Q(**{table_field: 'null'}))
            items = Sample.objects.filter(sampleid__in=selected).exclude(reduce(operator.or_, exclude_list)).order_by('sample_name')
            for item in items:
                myNode1 = {
                    'title': 'Sample: ' + item.sample_name,
                    'id': item.sampleid,
                    'tooltip': 'Project: ' + item.projectid.project_name,
                    'hideCheckbox': True,
                    'isFolder': False
                }
                myNode.append(myNode1)

        res = simplejson.dumps(myNode, encoding="Latin-1")
        return StreamingHttpResponse(res, content_type='application/json')


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
            'expand': False,
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
        sig_only = int(all["sig_only"])
        norm = int(all["normalize"])

        taxaString = all["taxa"]
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)
        metaDF = catAlphaDF(qs1, metaDict)

        myList = metaDF['sampleid'].tolist()
        mySet = list(set(myList))
        taxaDF = taxaProfileDF(mySet)

        factor = 'none'
        if norm == 1:
            factor = 'none'
        elif norm == 2:
            factor = 'min'
        elif norm == 3:
            factor = '10th percentile'
        elif norm == 4:
            factor = 'median'
        elif norm == 5:
            factor = 'mean'
        elif norm == 6:
            factor = '90th percentile'

        normDF = normalizeAlpha(taxaDF, taxaDict, mySet, factor)

        finalDF = metaDF.merge(normDF, on='sampleid', how='outer')
        finalDF[['count', 'rel_abund', 'rich', 'diversity']] = finalDF[['count', 'rel_abund', 'rich', 'diversity']].astype(float)
        pd.set_option('display.max_rows', finalDF.shape[0], 'display.max_columns', finalDF.shape[1], 'display.width', 1000)

        final_fieldList = []
        for key in metaDict:
            final_fieldList.append(key)

        finalDict = {}
        result = ""
        seriesList = []
        xAxisDict = {}
        yAxisDict = {}
        grouped1 = finalDF.groupby(['rank', 'taxa_name', 'taxa_id'])
        equal_error = 'no'
        for name1, group1 in grouped1:
            trtList = []
            valList = []
            grouped2 = pd.DataFrame()
            if button == 1:
                grouped2 = group1.groupby(final_fieldList)['count']
            elif button == 2:
                grouped2 = group1.groupby(final_fieldList)['rel_abund']
            elif button == 3:
                grouped2 = group1.groupby(final_fieldList)['rich']
                if group1['rich'].sum() == group1['rich'].count():
                    equal_error = 'yes'
            elif button == 4:
                grouped2 = group1.groupby(final_fieldList)['diversity']
            for name2, group2 in grouped2:
                if isinstance(name2, unicode):
                    trt = name2
                else:
                    trt = ' & '.join(list(name2))
                trtList.append(trt)
                valList.append(list(group2.T))

            D = Anova1way()
            if equal_error == 'no':
                try:
                    D.run(valList, conditions_list=trtList)
                    anova_error = 'no'
                except:
                    D['p'] = 1
                    anova_error = 'yes'
            else:
                D['p'] = 1
                anova_error = 'yes'

            if sig_only == 1:
                if D['p'] <= 0.05:
                    result = result + '===============================================\n'
                    result = result + 'Taxa level: ' + str(name1[0]) + '\n'
                    result = result + 'Taxa name: ' + str(name1[1]) + '\n'
                    if button == 1:
                        result = result + 'Dependent Variable: Sequence Reads' + '\n'
                    elif button == 2:
                        result = result + 'Dependent Variable: Relative Abundance' + '\n'
                    elif button == 3:
                        result = result + 'Dependent Variable: Species Richness' + '\n'
                    elif button == 4:
                        result = result + 'Dependent Variable: Shannon Diversity' + '\n'

                    indVar = ' x '.join(final_fieldList)
                    result = result + 'Independent Variable: ' + str(indVar) + '\n'

                    if equal_error == 'yes' or anova_error == 'yes':
                        result = result + 'Analysis cannot be performed...' + '\n'
                    else:
                        result = result + str(D) + '\n'
                    result = result + '===============================================\n'
                    result = result + '\n\n\n\n'

                    dataList = []
                    grouped2 = group1.groupby(final_fieldList).mean()

                    if button == 1:
                        dataList.extend(list(grouped2['count'].T))
                    elif button == 2:
                        dataList.extend(list(grouped2['rel_abund'].T))
                    elif button == 3:
                        dataList.extend(list(grouped2['rich'].T))
                    elif button == 4:
                        dataList.extend(list(grouped2['diversity'].T))

                    seriesDict = {}
                    seriesDict['name'] = str(name1[0]) + ": " + str(name1[1])
                    seriesDict['data'] = dataList
                    seriesList.append(seriesDict)

                    xTitle = {}
                    xTitle['text'] = indVar
                    xAxisDict['title'] = xTitle
                    xAxisDict['categories'] = trtList

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

            if sig_only == 0:
                result = result + '===============================================\n'
                result = result + 'Taxa level: ' + str(name1[0]) + '\n'
                result = result + 'Taxa name: ' + str(name1[1]) + '\n'
                if button == 1:
                    result = result + 'Dependent Variable: Sequence Reads' + '\n'
                elif button == 2:
                    result = result + 'Dependent Variable: Relative Abundance' + '\n'
                elif button == 3:
                    result = result + 'Dependent Variable: Species Richness' + '\n'
                elif button == 4:
                    result = result + 'Dependent Variable: Shannon Diversity' + '\n'

                indVar = ' x '.join(final_fieldList)
                result = result + 'Independent Variable: ' + str(indVar) + '\n'

                if equal_error == 'yes' or anova_error == 'yes':
                    result = result + 'Analysis cannot be performed...' + '\n'
                else:
                    result = result + str(D) + '\n'
                result = result + '===============================================\n'
                result = result + '\n\n\n\n'

                dataList = []
                grouped2 = group1.groupby(final_fieldList).mean()
                if button == 1:
                    dataList.extend(list(grouped2['count'].T))
                elif button == 2:
                    dataList.extend(list(grouped2['rel_abund'].T))
                elif button == 3:
                    dataList.extend(list(grouped2['rich'].T))
                elif button == 4:
                    dataList.extend(list(grouped2['diversity'].T))

                seriesDict = {}
                seriesDict['name'] = str(name1[0]) + ": " + str(name1[1])
                seriesDict['data'] = dataList
                seriesList.append(seriesDict)

                xTitle = {}
                xTitle['text'] = indVar
                xAxisDict['title'] = xTitle
                xAxisDict['categories'] = trtList

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
        finalDict['text'] = result
        if not seriesList:
            finalDict['empty'] = 0
        else:
            finalDict['empty'] = 1

        finalDict['finalDF'] = str(finalDF)
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
        sig_only = int(all["sig_only"])
        norm = int(all["normalize"])

        taxaString = all["taxa"]
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)
        metaDF = quantAlphaDF(qs1, metaDict)

        myList = metaDF['sampleid'].tolist()
        mySet = list(set(myList))
        taxaDF = taxaProfileDF(mySet)

        factor = 'none'
        if norm == 1:
            factor = 'none'
        elif norm == 2:
            factor = 'min'
        elif norm == 3:
            factor = '10th percentile'
        elif norm == 4:
            factor = 'median'
        elif norm == 5:
            factor = 'mean'
        elif norm == 6:
            factor = '90th percentile'

        final_fieldList = []
        for key, value in metaDict.items():
            final_fieldList.append(value)

        normDF = normalizeAlpha(taxaDF, taxaDict, mySet, factor)
        finalDF = metaDF.merge(normDF, on='sampleid', how='outer')
        finalDF[[final_fieldList[0], 'count', 'rel_abund', 'rich', 'diversity']] = finalDF[[final_fieldList[0], 'count', 'rel_abund', 'rich', 'diversity']].astype(float)
        pd.set_option('display.max_rows', finalDF.shape[0], 'display.max_columns', finalDF.shape[1], 'display.width', 1000)

        finalDict = {}
        seriesList = []
        xAxisDict = {}
        yAxisDict = {}
        grouped1 = finalDF.groupby(['rank', 'taxa_name', 'taxa_id'])
        for name1, group1 in grouped1:
            dataList = []
            x = []
            y = []
            if button == 1:
                dataList = group1[[final_fieldList[0], 'count']].values.tolist()
                x = group1[final_fieldList[0]].values.tolist()
                y = group1['count'].values.tolist()
            elif button == 2:
                dataList = group1[[final_fieldList[0], 'rel_abund']].values.tolist()
                x = group1[final_fieldList[0]].values.tolist()
                y = group1['rel_abund'].values.tolist()
            elif button == 3:
                dataList = group1[[final_fieldList[0], 'rich']].values.tolist()
                x = group1[final_fieldList[0]].values.tolist()
                y = group1['rich'].values.tolist()
            elif button == 4:
                dataList = group1[[final_fieldList[0], 'diversity']].values.tolist()
                x = group1[final_fieldList[0]].values.tolist()
                y = group1['diversity'].values.tolist()

            if max(x) == min(x):
                stop = 0
            else:
                stop = 1
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                p_value = "%0.3f" % p_value
                r_square = r_value * r_value
                r_square = "%0.4f" % r_square
                min_y = slope*min(x) + intercept
                max_y = slope*max(x) + intercept
                slope = "%.3E" % slope
                intercept = "%.3E" % intercept

                regrList = []
                regrList.append([min(x), min_y])
                regrList.append([max(x), max_y])

            if sig_only == 0:
                seriesDict = {}
                seriesDict['type'] = 'scatter'
                seriesDict['name'] = str(name1[0]) + ": " + str(name1[1])
                seriesDict['data'] = dataList
                seriesList.append(seriesDict)
                if stop == 0:
                    regDict = {}
                elif stop == 1:
                    regrDict = {}
                    regrDict['type'] = 'line'
                    regrDict['name'] = 'R2: ' + str(r_square) + '; p-value: ' + str(p_value) + '<br>' + '(y = ' + str(slope) + 'x' + ' + ' + str(intercept) + ')'
                    regrDict['data'] = regrList
                    seriesList.append(regrDict)

            if sig_only == 1:
                if p_value <= 0.05:
                    seriesDict = {}
                    seriesDict['type'] = 'scatter'
                    seriesDict['name'] = str(name1[0]) + ": " + str(name1[1])
                    seriesDict['data'] = dataList
                    seriesList.append(seriesDict)

                    regrDict = {}
                    regrDict['type'] = 'line'
                    regrDict['name'] = 'R2: ' + str(r_square) + '; p-value: ' + str(p_value) + '<br>' + '(y = ' + str(slope) + 'x' + ' + ' + str(intercept) + ')'
                    regrDict['data'] = regrList
                    seriesList.append(regrDict)

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
        if not seriesList:
            finalDict['empty'] = 0
        else:
            finalDict['empty'] = 1

        finalDict['finalDF'] = str(finalDF)
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
        norm = int(all["normalize"])
        PC1 = all["PC1"]
        PC2 = all["PC2"]

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)
        metaDF = catBetaMetaDF(qs1, metaDict)

        myList = metaDF['sampleid'].tolist()
        mySet = list(set(myList))
        taxaDF = taxaProfileDF(mySet)

        factor = 'none'
        factor = 'none'
        if norm == 1:
            factor = 'none'
        elif norm == 2:
            factor = 'min'
        elif norm == 3:
            factor = '10th percentile'
        elif norm == 4:
            factor = 'median'
        elif norm == 5:
            factor = 'mean'
        elif norm == 6:
            factor = '90th percentile'

        normDF = normalizeBeta(taxaDF, taxaLevel, mySet, factor)

        finalDF = metaDF.merge(normDF, on='sampleid', how='outer')
        pd.set_option('display.max_rows', finalDF.shape[0], 'display.max_columns', finalDF.shape[1], 'display.width', 1000)

        fieldList = []
        for key in metaDict:
            fieldList.append(key)

        sampleList = list(set(metaDF['sampleid'].tolist()))

        matrixDF = pd.DataFrame()
        if button == 1:
            matrixDF = finalDF.pivot_table(index='taxaid', columns='sampleid', values='count')
        elif button == 2:
            matrixDF = finalDF.pivot_table(index='taxaid', columns='sampleid', values='rel_abund')
        elif button == 3:
            matrixDF = finalDF.pivot_table(index='taxaid', columns='sampleid', values='rich')
        elif button == 4:
            matrixDF = finalDF.pivot_table(index='taxaid', columns='sampleid', values='diversity')

        datamtx = asarray(matrixDF[mySet].T)
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

        metaDF.set_index('sampleid', drop=True, inplace=True)
        pcoaDF = pd.DataFrame(coordinates, columns=axesList, index=sampleList)
        resultDF = metaDF.join(pcoaDF)
        pd.set_option('display.max_rows', resultDF.shape[0], 'display.max_columns', resultDF.shape[1], 'display.width', 1000)

        trtList = list(metaDF[fieldList[0]])
        bigf, p = permanova_oneway(dists, trtList, 1000)

        finalDict = {}
        seriesList = []
        xAxisDict = {}
        yAxisDict = {}
        grouped = resultDF.groupby(fieldList)
        for name, group in grouped:
            dataList = group[[PC1, PC2]].values.tolist()
            if isinstance(name, unicode):
                trt = name
            else:
                trt = ' & '.join(list(name))
            seriesDict = {}
            seriesDict['name'] = trt
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

        indVar = ' x '.join(fieldList)
        result = result + 'Independent Variable: ' + str(indVar) + '\n'

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

        if math.isnan(bigf):
            result = result + '===============================================\n'
            result = result + 'perMANOVA cannot be performed...' + '\n'
        else:
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

        nameList = list(metaDF['sample_name'])
        distsDF = pd.DataFrame(dists, columns=nameList, index=nameList)
        pd.set_option('display.max_rows', distsDF.shape[0], 'display.max_columns', distsDF.shape[1], 'display.width', 1000)
        finalDict['finalDF'] = str(distsDF)

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
        norm = int(all["normalize"])
        PC1 = all["PC1"]

        metaString = all["meta"]
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)
        metaDF = quantBetaMetaDF(qs1, metaDict)

        myList = metaDF['sampleid'].tolist()
        mySet = list(set(myList))
        taxaDF = taxaProfileDF(mySet)

        factor = 'none'
        factor = 'none'
        if norm == 1:
            factor = 'none'
        elif norm == 2:
            factor = 'min'
        elif norm == 3:
            factor = '10th percentile'
        elif norm == 4:
            factor = 'median'
        elif norm == 5:
            factor = 'mean'
        elif norm == 6:
            factor = '90th percentile'

        normDF = normalizeBeta(taxaDF, taxaLevel, mySet, factor)

        finalDF = metaDF.merge(normDF, on='sampleid', how='outer')
        pd.set_option('display.max_rows', finalDF.shape[0], 'display.max_columns', finalDF.shape[1], 'display.width', 1000)

        fieldList = []
        for key, value in metaDict.items():
            fieldList.append(value)

        sampleList = list(set(metaDF['sampleid'].tolist()))

        matrixDF = pd.DataFrame()
        if button == 1:
            matrixDF = finalDF.pivot_table(index='taxaid', columns='sampleid', values='count')
        elif button == 2:
            matrixDF = finalDF.pivot_table(index='taxaid', columns='sampleid', values='rel_abund')
        elif button == 3:
            matrixDF = finalDF.pivot_table(index='taxaid', columns='sampleid', values='rich')
        elif button == 4:
            matrixDF = finalDF.pivot_table(index='taxaid', columns='sampleid', values='diversity')

        datamtx = asarray(matrixDF[mySet].T)
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

        metaDF.set_index('sampleid', drop=True, inplace=True)
        pcoaDF = pd.DataFrame(coordinates, columns=axesList, index=sampleList)
        resultDF = metaDF.join(pcoaDF)
        pd.set_option('display.max_rows', resultDF.shape[0], 'display.max_columns', resultDF.shape[1], 'display.width', 1000)


        finalDict = {}
        seriesList = []
        xAxisDict = {}
        yAxisDict = {}
        dataList = resultDF[[PC1, fieldList[0]]].values.tolist()

        seriesDict = {}
        seriesDict['type'] = 'scatter'
        seriesDict['name'] = fieldList
        seriesDict['data'] = dataList
        seriesList.append(seriesDict)

        x = resultDF[PC1].values.tolist()
        y = resultDF[fieldList[0]].values.tolist()

        if max(x) == min(x):
            stop = 0
        else:
            stop = 1
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            p_value = "%0.3f" % p_value
            r_square = r_value * r_value
            r_square = "%0.4f" % r_square
            min_y = slope*min(x) + intercept
            max_y = slope*max(x) + intercept
            slope = "%.3E" % slope
            intercept = "%.3E" % intercept

            regrList = []
            regrList.append([min(x), min_y])
            regrList.append([max(x), max_y])

            if stop == 0:
                regDict = {}
            elif stop == 1:
                regrDict = {}
                regrDict['type'] = 'line'
                regrDict['name'] = 'R2: ' + str(r_square) + '; p-value: ' + str(p_value) + '<br>' + '(y = ' + str(slope) + 'x' + ' + ' + str(intercept) + ')'
                regrDict['data'] = regrList
                seriesList.append(regrDict)

        xTitle = {}
        xTitle['text'] = PC1
        xAxisDict['title'] = xTitle

        yTitle = {}
        yTitle['text'] = fieldList[0]
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

        nameList = list(metaDF['sample_name'])
        distsDF = pd.DataFrame(dists, columns=nameList, index=nameList)
        pd.set_option('display.max_rows', distsDF.shape[0], 'display.max_columns', distsDF.shape[1], 'display.width', 1000)
        finalDict['finalDF'] = str(distsDF)

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')
