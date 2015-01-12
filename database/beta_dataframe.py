from django.db.models import Q
import math      ### pycharm doesn't recognize, but this is required
import numpy as np      ### pycharm doesn't recognize, but this is required
from numpy import *
from numpy.random import mtrand
import operator
import pandas as pd
from scipy.spatial.distance import *


def catBetaMetaDF(qs1, metaDict):
    sampleTableList = ['sample_name', 'organism', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc_country', 'geo_loc_state', 'geo_loc_city', 'geo_loc_farm', 'geo_loc_plot', 'material']
    collectTableList = ['depth', 'pool_dna_extracts', 'samp_collection_device', 'sieving', 'storage_cond']
    soil_classTableList = ['drainage_class', 'fao_class', 'horizon', 'local_class', 'profile_position', 'slope_aspect', 'soil_type', 'texture_class']
    mgtTableList = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
    usrTableList = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6']

    metaDF = pd.DataFrame()
    for key in metaDict:
        value = metaDict[key]
        args_list = []
        field_list = []

        if key in sampleTableList:
            field_list.append('sampleid')
            if key != 'sample_name':
                field_list.append('sample_name')
            field = str(key)
            field_list.append(field)
            if type(value) is unicode:
                args_list.append(Q(**{field: value}))
            else:
                for item in value:
                    args_list.append(Q(**{field: item}))
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).filter(reduce(operator.or_, args_list)).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            if metaDF.empty:
                metaDF = tempDF
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in collectTableList:
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'collect__' + str(key)
            field_list.append(field)
            if type(value) is unicode:
                args_list.append(Q(**{field: value}))
            else:
                for item in value:
                    args_list.append(Q(**{field: item}))
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).filter(reduce(operator.or_, args_list)).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: key}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in soil_classTableList:
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'soil_class__' + str(key)
            field_list.append(field)
            if type(value) is unicode:
                args_list.append(Q(**{field: value}))
            else:
                for item in value:
                    args_list.append(Q(**{field: item}))
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).filter(reduce(operator.or_, args_list)).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: key}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in mgtTableList:
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'management__' + str(key)
            field_list.append(field)
            if type(value) is unicode:
                args_list.append(Q(**{field: value}))
            else:
                for item in value:
                    args_list.append(Q(**{field: item}))
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).filter(reduce(operator.or_, args_list)).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: key}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

        elif key in usrTableList:
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'user__' + str(key)
            field_list.append(field)
            if type(value) is unicode:
                args_list.append(Q(**{field: value}))
            else:
                for item in value:
                    args_list.append(Q(**{field: item}))
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).filter(reduce(operator.or_, args_list)).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: key}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

    return metaDF


def quantBetaMetaDF(qs1, metaDict):
    metaDF = pd.DataFrame()
    final_fieldList = []
    for key in metaDict:
        value = metaDict[key]
        field_list = []

        if key == 'mimark':
            field_list.append('sampleid')
            field_list.append('sample_name')
            field_list.append(value)
            final_fieldList.append(value)
            exclude_list = []
            exclude_list.append(Q(**{value: 'null'}))
            qs2 = qs1.values(*field_list).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            if metaDF.empty:
                metaDF = tempDF
                metaDF[value] = metaDF[value].astype(float)
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')
                metaDF[value] = metaDF[value].astype(float)


        elif key == 'collect':
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'collect__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
                metaDF[value] = metaDF[value].astype(float)
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')
                metaDF[value] = metaDF[value].astype(float)

        elif key == 'climate':
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'climate__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
                metaDF[value] = metaDF[value].astype(float)
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')
                metaDF[value] = metaDF[value].astype(float)

        elif key == 'soil_class':
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'soil_class__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
                metaDF[value] = metaDF[value].astype(float)
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')
                metaDF[value] = metaDF[value].astype(float)

        elif key == 'soil_nutrient':
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'soil_nutrient__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
                metaDF[value] = metaDF[value].astype(float)
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')
                metaDF[value] = metaDF[value].astype(float)

        elif key == 'microbial':
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'microbial__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
                metaDF[value] = metaDF[value].astype(float)
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')
                metaDF[value] = metaDF[value].astype(float)

        elif key == 'user':
            field_list.append('sampleid')
            field_list.append('sample_name')
            field = 'user__' + str(value)
            field_list.append(field)
            final_fieldList.append(value)
            exclude_list = []
            exclude_list.append(Q(**{field: 'null'}))
            qs2 = qs1.values(*field_list).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: value}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
                metaDF[value] = metaDF[value].astype(float)
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')
                metaDF[value] = metaDF[value].astype(float)

    return metaDF


def normalizeBeta(df, taxaLevel, mySet, factor):
    df2 = df.reset_index()
    taxaID = ['kingdomid', 'phylaid', 'classid', 'orderid', 'familyid', 'genusid', 'speciesid']

    field = ''
    rank = ''
    if taxaLevel == 1:
        rank = 'Kingdom'
        field = 'kingdomid'
    elif taxaLevel == 2:
        rank = 'Phyla'
        field = 'phylaid'
    elif taxaLevel == 3:
        rank = 'Class'
        field = 'classid'
    elif taxaLevel == 4:
        rank = 'Order'
        field = 'orderid'
    elif taxaLevel == 5:
        rank = 'Family'
        field = 'familyid'
    elif taxaLevel == 6:
        rank = 'Genus'
        field = 'genusid'
    elif taxaLevel == 7:
        rank = 'Species'
        field = 'speciesid'

    countDF = pd.DataFrame()
    if factor in ['min', '10th percentile', '25th percentile', 'median']:
        countDF = df2[taxaID].reset_index(drop=True)
        col_totals = np.array(df.sum(axis=0))

        reads = 0
        if factor == 'min':
            reads = int(np.min(col_totals))
        elif factor == '10th percentile':
            reads = int(np.percentile(col_totals, 10))
        elif factor == '25th percentile':
            reads = int(np.percentile(col_totals, 25))
        elif factor == 'median':
            reads = int(np.median(col_totals))

        for i in mySet:
            arr = asarray(df[i].T)
            cols = shape(arr)

            sample = arr.astype(dtype=np.float64)
            myLambda = 0.1

            #Lidstone's approximation
            prob = (sample + myLambda) / (sample.sum() + cols[0] * myLambda)

            final = np.zeros(cols)
            for j in range(1, reads):
                sub = np.random.mtrand.choice(range(sample.size), size=1, replace=False, p=prob)
                temp = np.zeros(cols)
                np.put(temp, sub, 1)
                final = np.add(final, temp)

            tempDF = pd.DataFrame(final, columns=[i])
            countDF = countDF.join(tempDF)
    elif factor == 'none':
        countDF = df2.reset_index(drop=True)

    relabundDF = countDF[taxaID]
    binaryDF = countDF[taxaID]
    diversityDF = countDF[taxaID]
    for i in mySet:
        relabundDF[i] = countDF[i].div(countDF[i].sum(axis=1), axis=0)
        binaryDF[i] = countDF[i].apply(lambda x: 1 if x != 0 else 0)
        diversityDF[i] = relabundDF[i].apply(lambda x: -1 * x * math.log(x) if x > 0 else 0)

    normDF = pd.DataFrame(columns=['sampleid', 'rank', 'count', 'rel_abund', 'rich', 'diversity'])
    for i in mySet:
        tmpDF = pd.DataFrame()
        tmpDF['count'] = countDF.groupby(field)[i].sum()
        tmpDF['rel_abund'] = relabundDF.groupby(field)[i].sum()
        tmpDF['rich'] = binaryDF.groupby(field)[i].sum()
        tmpDF['diversity'] = diversityDF.groupby(field)[i].sum()
        tmpDF['sampleid'] = i
        tmpDF['rank'] = rank
        tmpDF.reset_index(inplace=True)
        normDF = normDF.append(tmpDF)
    normDF.rename(columns={field: 'taxaid'}, inplace=True)

    return normDF
