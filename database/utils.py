import numpy as np
import operator
import os
import pandas as pd
import pickle
import shutil
from collections import defaultdict
from django.db.models import Q
from models import Project, Sample, Collect, Soil_class, Management, User
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile
from models import ProfileKingdom, ProfilePhyla, ProfileClass, ProfileOrder, ProfileFamily, ProfileGenus, ProfileSpecies


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


def catDataFrame(qs1, taxaDict, metaDict):
    sampleTableList = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc', 'material']
    collectTableList = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
    soil_classTableList = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
    mgtTableList = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
    usrTableList = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']

    finalDF = pd.DataFrame()
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
                metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

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
                metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

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
                metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

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
                metaDF = pd.merge(tempDF, metaDF, on='sampleid', how='outer')

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
                taxaDF['rank'] = 1
                taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Phyla'
                taxaDF['rank'] = 2
                taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'classid', 'classid__className', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Class'
                taxaDF['rank'] = 3
                taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Order'
                taxaDF['rank'] = 4
                taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Family'
                taxaDF['rank'] = 5
                taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Genus'
                taxaDF['rank'] = 6
                taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values()
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Species'
                taxaDF['rank'] = '7'
                taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Species', inplace=True)
                mergeDF['rank'].fillna(7, inplace=True)
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
                    taxaDF['rank'] = 1
                    taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Phyla'
                    taxaDF['rank'] = 2
                    taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'classid', 'classid__className', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Class'
                    taxaDF['rank'] = 3
                    taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Order'
                    taxaDF['rank'] = 4
                    taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Family'
                    taxaDF['rank'] = 5
                    taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Genus'
                    taxaDF['rank'] = 6
                    taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Species'
                    taxaDF['rank'] = 7
                    taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
    finalDF[['rich', 'rel_abund']] = finalDF[['rich', 'rel_abund']].astype(float)
    return finalDF


def quantDataFrame(qs1, taxaDict, metaDict):
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
                taxaDF['rank'] = 1
                taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Phyla'
                taxaDF['rank'] = 2
                taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'classid', 'classid__className', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Class'
                taxaDF['rank'] = 3
                taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Order'
                taxaDF['rank'] = 4
                taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Famiily'
                taxaDF['rank'] = 5
                taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values('sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich')
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Genus'
                taxaDF['rank'] = 6
                taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
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
                qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: value})).values()
                taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich'])
                taxaDF['taxa'] = 'Species'
                taxaDF['rank'] = 7
                taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                mergeDF['rel_abund'].fillna(0, inplace=True)
                mergeDF['rich'].fillna(0, inplace=True)
                mergeDF['taxa'].fillna('Species', inplace=True)
                mergeDF['rank'].fillna(7, inplace=True)
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
                    taxaDF['rank'] = 1
                    taxaDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomid__kingdomName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfilePhyla.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'phylaid', 'phylaid__phylaName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Phyla'
                    taxaDF['rank'] = 2
                    taxaDF.rename(columns={'phylaid': 'taxa_id', 'phylaid__phylaName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileClass.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'classid', 'classid__className', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'classid', 'classid__className', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Class'
                    taxaDF['rank'] = 3
                    taxaDF.rename(columns={'classid': 'taxa_id', 'classid__className': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileOrder.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'orderid', 'orderid__orderName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Order'
                    taxaDF['rank'] = 4
                    taxaDF.rename(columns={'orderid': 'taxa_id', 'orderid__orderName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileFamily.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'familyid', 'familyid__familyName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Family'
                    taxaDF['rank'] = 5
                    taxaDF.rename(columns={'familyid': 'taxa_id', 'familyid__familyName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileGenus.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'genusid', 'genusid__genusName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Genus'
                    taxaDF['rank'] = 6
                    taxaDF.rename(columns={'genusid': 'taxa_id', 'genusid__genusName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
                    qs1 = ProfileSpecies.objects.filter(sampleid__in=myset).filter(Q(**{field: item})).values('sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich')
                    taxaDF = pd.DataFrame.from_records(qs1, columns=['sampleid', 'speciesid', 'speciesid__speciesName', 'rel_abund', 'rich'])
                    taxaDF['taxa'] = 'Species'
                    taxaDF['rank'] = 7
                    taxaDF.rename(columns={'speciesid': 'taxa_id', 'speciesid__speciesName': 'taxa_name'}, inplace=True)
                    mergeDF = pd.merge(metaDF, taxaDF, on='sampleid', how='outer')
                    mergeDF['rel_abund'].fillna(0, inplace=True)
                    mergeDF['rich'].fillna(0, inplace=True)
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
    finalDF[['x-value', 'rich', 'rel_abund']] = finalDF[['x-value', 'rich', 'rel_abund']].astype(float)
    return finalDF
