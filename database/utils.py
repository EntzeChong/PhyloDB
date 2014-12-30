import operator
import os
import pickle
import pandas as pd
import numpy as np
from numpy import asarray, shape, zeros
import shutil
from collections import defaultdict
from django.db.models import Q
from models import Project
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile
from models import ProfileKingdom, ProfilePhyla, ProfileClass, ProfileOrder, ProfileFamily, ProfileGenus, ProfileSpecies
from scipy.spatial.distance import *
from scipy import stats
import random as r
from itertools import permutations, product, chain


def handle_uploaded_file(f, path, name):
    if not os.path.exists(path):
        os.makedirs(path)
    dest = "/".join([str(path), str(name)])
    with open(str(dest), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def remove_list(request):
    items = request.POST.getlist('chkbx')
    for item in items:
        q = Project.objects.get(projectid=item)
        shutil.rmtree(q.path)
        Project.objects.get(projectid=item).delete()


def multidict(ordered_pairs):
    d = defaultdict(list)
    for k, v in ordered_pairs:
        d[k].append(v)

    for k, v in d.items():
        if len(v) == 1:
            d[k] = v[0]
    return dict(d)


def catAlphaDF(qs1, metaDict):
    sampleTableList = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc', 'material']
    collectTableList = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
    soil_classTableList = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
    mgtTableList = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
    usrTableList = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']

    metaDF = pd.DataFrame()
    for key, value in metaDict.items():
        args_list = []
        field_list = []

        if key in sampleTableList:
            field_list.append('sampleid')
            field = str(key)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in collectTableList:
            field_list.append('sampleid')
            field = 'collect__' + str(key)
            field_list.append(field)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in soil_classTableList:
            field_list.append('sampleid')
            field = 'soil_class__' + str(key)
            field_list.append(field)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in mgtTableList:
            field_list.append('sampleid')
            field = 'management__' + str(key)
            field_list.append(field)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in usrTableList:
            field_list.append('sampleid')
            field = 'user__' + str(key)
            field_list.append(field)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

    return metaDF


def quantAlphaDF(qs1, metaDict):
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

    return metaDF


def alphaTaxaDF(metaDF, taxaDict):
    graph_selected = metaDF['sampleid'].tolist()
    myset = list(set(graph_selected))
    finalDF = pd.DataFrame()

    ## Filter the taxonomy profile tables
    for key, value in taxaDict.items():
        if type(value) is unicode:
            if key == 'Kingdom':
                field = 'kingdomid'
                qs1 = ProfileKingdom.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'kingdomid', 'kingdomid__kingdomName', 'count', 'rel_abund', 'rich', 'diversity')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'kingdomid', 'kingdomid__kingdomName', 'count', 'rel_abund', 'rich', 'diversity'])
                taxaDF['taxa'] = 'Kingdom'
                taxaDF['rank'] = 1
                taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['count'].fillna(0, inplace=True)
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['diversity'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Kingdom', inplace=True)
                mergeDF['rank'].fillna(1, inplace=True)
                name = Kingdom.objects.filter(Q(**{'kingdomid': value})).values('kingdomid', 'kingdomName')
                mergeDF['taxa_id'].fillna(name[0]['kingdomid'], inplace=True)
                mergeDF['taxa_name'].fillna(name[0]['kingdomName'], inplace=True)
                if finalDF.empty:
                    finalDF = mergeDF
                else:
                    finalDF = finalDF.append(mergeDF)

            elif key == 'Phyla':
                field = 'phylaid'
                qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'count', 'rel_abund', 'rich', 'diversity')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'count', 'rel_abund', 'rich', 'diversity'])
                taxaDF['taxa'] = 'Phyla'
                taxaDF['rank'] = 2
                taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['count'].fillna(0, inplace=True)
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['diversity'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Phyla', inplace=True)
                mergeDF['rank'].fillna(2, inplace=True)
                name = Phyla.objects.filter(Q(**{'phylaid': value})).values('phylaid', 'phylaName')
                mergeDF['taxa_id'].fillna(name[0]['phylaid'], inplace=True)
                mergeDF['taxa_name'].fillna(name[0]['phylaName'], inplace=True)
                if finalDF.empty:
                    finalDF = mergeDF
                else:
                    finalDF = finalDF.append(mergeDF)

            elif key == 'Class':
                field = 'classid'
                qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'classid', 'classid__className', 'count', 'rel_abund', 'rich', 'diversity')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'count', 'rel_abund', 'rich', 'diversity'])
                taxaDF['taxa'] = 'Class'
                taxaDF['rank'] = 3
                taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['count'].fillna(0, inplace=True)
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['diversity'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Class', inplace=True)
                mergeDF['rank'].fillna(3, inplace=True)
                name = Class.objects.filter(Q(**{'classid': value})).values('classid', 'className')
                mergeDF['taxa_id'].fillna(name[0]['classid'], inplace=True)
                mergeDF['taxa_name'].fillna(name[0]['className'], inplace=True)
                if finalDF.empty:
                    finalDF = mergeDF
                else:
                    finalDF = finalDF.append(mergeDF)

            elif key == 'Order':
                field = 'orderid'
                qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'orderid', 'orderid__orderName', 'count', 'rel_abund', 'rich', 'diversity')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'count', 'rel_abund', 'rich', 'diversity'])
                taxaDF['taxa'] = 'Order'
                taxaDF['rank'] = 4
                taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['count'].fillna(0, inplace=True)
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['diversity'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Order', inplace=True)
                mergeDF['rank'].fillna(4, inplace=True)
                name = Order.objects.filter(Q(**{'orderid': value})).values('orderid', 'orderName')
                mergeDF['taxa_id'].fillna(name[0]['orderid'], inplace=True)
                mergeDF['taxa_name'].fillna(name[0]['orderName'], inplace=True)
                if finalDF.empty:
                    finalDF = mergeDF
                else:
                    finalDF = finalDF.append(mergeDF)

            elif key == 'Family':
                field = 'familyid'
                qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'familyid', 'familyid__familyName', 'count', 'rel_abund', 'rich', 'diversity')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'count', 'rel_abund', 'rich', 'diversity'])
                taxaDF['taxa'] = 'Family'
                taxaDF['rank'] = 5
                taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['count'].fillna(0, inplace=True)
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['diversity'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Family', inplace=True)
                mergeDF['rank'].fillna(5, inplace=True)
                name = Family.objects.filter(Q(**{'familyid': value})).values('familyid', 'familyName')
                mergeDF['taxa_id'].fillna(name[0]['familyid'], inplace=True)
                mergeDF['taxa_name'].fillna(name[0]['familyName'], inplace=True)
                if finalDF.empty:
                    finalDF = mergeDF
                else:
                    finalDF = finalDF.append(mergeDF)

            elif key == 'Genus':
                field = 'genusid'
                qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'genusid', 'genusid__genusName', 'count', 'rel_abund', 'rich', 'diversity')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'count', 'rel_abund', 'rich', 'diversity'])
                taxaDF['taxa'] = 'Genus'
                taxaDF['rank'] = 6
                taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['count'].fillna(0, inplace=True)
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['diversity'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Genus', inplace=True)
                mergeDF['rank'].fillna(6, inplace=True)
                name = Genus.objects.filter(Q(**{'genusid': value})).values('genusid', 'genusName')
                mergeDF['taxa_id'].fillna(name[0]['genusid'], inplace=True)
                mergeDF['taxa_name'].fillna(name[0]['genusName'], inplace=True)
                if finalDF.empty:
                    finalDF = mergeDF
                else:
                    finalDF = finalDF.append(mergeDF)

            elif key == 'Species':
                field = 'speciesid'
                qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'speciesid', 'speciesid__speciesName', 'count', 'rel_abund', 'rich', 'diversity')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'count', 'rel_abund', 'rich', 'diversity'])
                taxaDF['taxa'] = 'Species'
                taxaDF['rank'] = 7
                taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['count'].fillna(0, inplace=True)
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['diversity'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Species', inplace=True)
                mergeDF['rank'].fillna(7, inplace=True)
                name = Species.objects.filter(Q(**{'speciesid': value})).values('speciesid', 'speciesName')

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
                    qs1 = ProfileKingdom.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'kingdomid', 'kingdomid__kingdomName', 'count', 'rel_abund', 'rich', 'diversity')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'kingdomid', 'kingdomid__kingdomName', 'count', 'rel_abund', 'rich', 'diversity'])
                    taxaDF['taxa'] = 'Kingdom'
                    taxaDF['rank'] = 1
                    taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['count'].fillna(0, inplace=True)
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['diversity'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Kingdom', inplace=True)
                    mergeDF['rank'].fillna(1, inplace=True)
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
                    qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'count', 'rel_abund', 'rich', 'diversity')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'count', 'rel_abund', 'rich', 'diversity'])
                    taxaDF['taxa'] = 'Phyla'
                    taxaDF['rank'] = 2
                    taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['count'].fillna(0, inplace=True)
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['diversity'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Phyla', inplace=True)
                    mergeDF['rank'].fillna(2, inplace=True)
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
                    qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'classid', 'classid__className', 'count', 'rel_abund', 'rich', 'diversity')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'count', 'rel_abund', 'rich', 'diversity'])
                    taxaDF['taxa'] = 'Class'
                    taxaDF['rank'] = 3
                    taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['count'].fillna(0, inplace=True)
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['diversity'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Class', inplace=True)
                    mergeDF['rank'].fillna(3, inplace=True)
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
                    qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'orderid', 'orderid__orderName', 'count', 'rel_abund', 'rich', 'diversity')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'count', 'rel_abund', 'rich', 'diversity'])
                    taxaDF['taxa'] = 'Order'
                    taxaDF['rank'] = 4
                    taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['count'].fillna(0, inplace=True)
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['diversity'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Order', inplace=True)
                    mergeDF['rank'].fillna(4, inplace=True)
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
                    qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'familyid', 'familyid__familyName', 'count', 'rel_abund', 'rich', 'diversity')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'count', 'rel_abund', 'rich', 'diversity'])
                    taxaDF['taxa'] = 'Family'
                    taxaDF['rank'] = 5
                    taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['count'].fillna(0, inplace=True)
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['diversity'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Family', inplace=True)
                    mergeDF['rank'].fillna(5, inplace=True)
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
                    qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'genusid', 'genusid__genusName', 'count', 'rel_abund', 'rich', 'diversity')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'count', 'rel_abund', 'rich', 'diversity'])
                    taxaDF['taxa'] = 'Genus'
                    taxaDF['rank'] = 6
                    taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['count'].fillna(0, inplace=True)
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['diversity'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Genus', inplace=True)
                    mergeDF['rank'].fillna(6, inplace=True)
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
                    qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'speciesid', 'speciesid__speciesName', 'count', 'rel_abund', 'rich', 'diversity')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'count', 'rel_abund', 'rich', 'diversity'])
                    taxaDF['taxa'] = 'Species'
                    taxaDF['rank'] = 7
                    taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['count'].fillna(0, inplace=True)
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
                    mergeDF['diversity'].fillna(0, inplace=True)
                    mergeDF['taxa'].fillna('Species', inplace=True)
                    mergeDF['rank'].fillna(7, inplace=True)
                    name = Species.objects.filter(Q(**{'speciesid': item})).values('speciesid', 'speciesName')
                    mergeDF['taxa_id'].fillna(name[0]['speciesid'], inplace=True)
                    mergeDF['taxa_name'].fillna(name[0]['speciesName'], inplace=True)
                    if finalDF.empty:
                        finalDF = mergeDF
                    else:
                        finalDF = finalDF.append(mergeDF)

    # Set datatypes
    finalDF[['count', 'rel_abund', 'rich', 'diversity']] = finalDF[['count', 'rel_abund', 'rich', 'diversity']].astype(float)
    return finalDF


def catBetaMetaDF(qs1, metaDict):
    sampleTableList = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc', 'material']
    collectTableList = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
    soil_classTableList = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
    mgtTableList = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
    usrTableList = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']

    metaDF = pd.DataFrame()
    for key, value in metaDict.items():
        args_list = []
        field_list = []

        if key in sampleTableList:
            field_list.append('sampleid')
            field = str(key)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in collectTableList:
            field_list.append('sampleid')
            field = 'collect__' + str(key)
            field_list.append(field)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in soil_classTableList:
            field_list.append('sampleid')
            field = 'soil_class__' + str(key)
            field_list.append(field)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in mgtTableList:
            field_list.append('sampleid')
            field = 'management__' + str(key)
            field_list.append(field)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in usrTableList:
            field_list.append('sampleid')
            field = 'user__' + str(key)
            field_list.append(field)
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
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

    return metaDF


def quantBetaMetaDF(qs1, metaDict):
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
#            tempDF.rename(columns={value: 'x-value'}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key == 'collect':
            field_list.append('sampleid')
            field = 'collect__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            qs2 = qs1.values(*field_list)
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key == 'climate':
            field_list.append('sampleid')
            field = 'climate__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            qs2 = qs1.values(*field_list)
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key == 'soil_class':
            field_list.append('sampleid')
            field = 'soil_class__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            qs2 = qs1.values(*field_list)
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key == 'soil_nutrient':
            field_list.append('sampleid')
            field = 'soil_nutrient__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            qs2 = qs1.values(*field_list)
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key == 'microbial':
            field_list.append('sampleid')
            field = 'microbial__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            qs2 = qs1.values(*field_list)
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key == 'user':
            field_list.append('sampleid')
            field = 'user__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            qs2 = qs1.values(*field_list)
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

    return metaDF


def betaTaxaDF(metaDF, myset, taxaLevel):
    taxaDF = pd.DataFrame()
    if taxaLevel == 2:
        qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).values('sampleid', 'phylaid', 'count', 'rel_abund', 'rich', 'diversity')
        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'count', 'rel_abund', 'rich', 'diversity'])
        taxaDF.rename(columns={'phylaid': 'taxaid'}, inplace=True)
    elif taxaLevel == 3:
        qs1 = ProfileClass.objects.filter(sampleid__in=myset).values('sampleid', 'classid', 'count', 'rel_abund', 'rich', 'diversity')
        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'count', 'rel_abund', 'rich', 'diversity'])
        taxaDF.rename(columns={'classid': 'taxaid'}, inplace=True)
    elif taxaLevel == 4:
        qs1 = ProfileOrder.objects.filter(sampleid__in=myset).values('sampleid', 'orderid', 'count', 'rel_abund', 'rich', 'diversity')
        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'count', 'rel_abund', 'rich', 'diversity'])
        taxaDF.rename(columns={'orderid': 'taxaid'}, inplace=True)
    elif taxaLevel == 5:
        qs1 = ProfileFamily.objects.filter(sampleid__in=myset).values('sampleid', 'familyid', 'count', 'rel_abund', 'rich', 'diversity')
        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'count', 'rel_abund', 'rich', 'diversity'])
        taxaDF.rename(columns={'familyid': 'taxaid'}, inplace=True)
    elif taxaLevel == 6:
        qs1 = ProfileGenus.objects.filter(sampleid__in=myset).values('sampleid', 'genusid', 'count', 'rel_abund', 'rich', 'diversity')
        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'count', 'rel_abund', 'rich', 'diversity'])
        taxaDF.rename(columns={'genusid': 'taxaid'}, inplace=True)
    elif taxaLevel == 7:
        qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).values('sampleid', 'speciesid', 'count', 'rel_abund', 'rich', 'diversity')
        taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'count', 'rel_abund', 'rich', 'diversity'])
        taxaDF.rename(columns={'speciesid': 'taxaid'}, inplace=True)

    finalDF = metaDF.merge(taxaDF, on='sampleid', how='outer')
    finalDF['count'].fillna(0, inplace=True)
    finalDF['rel_abund'].fillna(0, inplace=True)
    finalDF['rich'].fillna(0, inplace=True)
    finalDF['diversity'].fillna(0, inplace=True)
    return finalDF


def principalComponents(matrix):
    deviationMatrix = (matrix.T - np.mean(matrix, axis=1)).T
    covarianceMatrix = np.cov(deviationMatrix)
    eigenvalues, principalComponents = np.linalg.eig(covarianceMatrix)

    indexList = np.argsort(-eigenvalues)
    eigenvalues = eigenvalues[indexList]
    principalComponents = principalComponents[:, indexList]
    return eigenvalues, principalComponents


stats.ss = lambda l: sum(a*a for a in l)
def above_diagonal(n):
    row = xrange(n)
    for i in row:
        for j in xrange(i+1, n):
            yield i, j


def select_ss(dm, levels,  included):
    bign = len(dm)
    distances = (dm[i][j] for i, j in above_diagonal(bign) if included(levels[i], levels[j]))
    return stats.ss(distances)


def permanova_oneway(dm, levels, permutations=200):
    bigf = f_oneway(dm, levels)
    above = below = 0
    nf = 0
    shuffledlevels = list(levels)
    for i in xrange(permutations):
        r.shuffle(shuffledlevels)
        f = f_oneway(dm, shuffledlevels)
        if f >= bigf:
            above += 1
    p = float(above/float(permutations))
    return bigf, p


def f_oneway(dm, levels):
    bign = float(len(levels))
    dm = np.asarray(dm)
    a = len(set(levels))
    n = float(bign/a)
    sst = np.sum(stats.ss(r) for r in (s[n+1:] for n, s in enumerate(dm[:-1])))/bign
    ssw = np.sum((dm[i][j]**2 for i, j in product(xrange(len(dm)), xrange(1, len(dm))) if i < j and levels[i] == levels[j]))/n
    ssa = sst - ssw
    fstat = (ssa/float(a-1))/(ssw/float(bign-a))
    return fstat


def permanova_twoway(dm, levels, permutations=200):
    bigf_i, bigf_a, bigf_b = f_twoway(dm, levels)
    above_i = above_a = above_b = 0
    shuffledlevels = list(levels)

    a_levels = list([l[0] for l in levels])
    b_levels = list([l[1] for l in levels])

    for i in xrange(permutations):
        r.shuffle(shuffledlevels)
        f_i, f_a, f_b = f_twoway(dm,shuffledlevels)
        if f_i > bigf_i:
            above_i += 1
    for i in xrange(permutations):
        r.shuffle(a_levels)
        f_i, f_a, f_b = f_twoway(dm,zip(a_levels, [l[1] for l in levels]))
        if f_a > bigf_a:
            above_a += 1
    for i in xrange(permutations):
        r.shuffle(b_levels)
        f_i, f_a, f_b = f_twoway(dm, zip([l[0] for l in levels], b_levels))
        if f_b > bigf_b:
            above_b += 1
    p_i, p_a, p_b = [above/float(permutations) for above in [above_i, above_a, above_b]]
    return bigf_a, float(p_a), bigf_b, float(p_b), bigf_i, float(p_i)


def f_twoway(dm, levels):
    bign = len(levels)
    dm = np.asarray(dm)
    l = len(set(levels))
    a = len(set([l[0] for l in levels]))
    b = len(set([l[1] for l in levels]))
    n = bign/float(a*b)

    sst = stats.ss(chain(*(r[i+1:] for i,r in enumerate(dm))))/float(bign)
    ssr = select_ss(dm, levels, lambda a,b: a==b)/float(n)
    sswa = select_ss(dm, levels, lambda a,b: a[0] == b[0])/float(b*n)
    sswb = select_ss(dm, levels, lambda a,b: a[1] == b[1])/float(a*n)
    ssa = sst - sswa
    ssb = sst - sswb
    ssab = sst - ssa - ssb - ssr

    f_interaction = float((ssab/float((a-1)*(b-1)))/(ssr/float(bign - a*b)))
    f_a = float((ssa/float((a-1)))/(ssr/float(bign - a*b)))
    f_b = float((ssb/float((b-1)))/(ssr/float(bign - a*b)))
    return (f_interaction, f_a, f_b)
