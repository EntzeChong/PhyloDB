from django.db.models import Q
import math                 ### pycharm doesn't recognize, but this is required
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species
import numpy as np          ### pycharm doesn't recognize, but this is required
from numpy import *
from numpy.random import mtrand
import operator
import pandas as pd
from scipy.spatial.distance import *


def catAlphaMetaDF(qs1, metaDict):
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
            qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list).exclude(reduce(operator.or_, exclude_list))
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
            qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list).exclude(reduce(operator.or_, exclude_list))
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
            qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list).exclude(reduce(operator.or_, exclude_list))
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
            qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list).exclude(reduce(operator.or_, exclude_list))
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
            qs2 = qs1.filter(reduce(operator.or_, args_list)).values(*field_list).exclude(reduce(operator.or_, exclude_list))
            tempDF = pd.DataFrame.from_records(qs2, columns=field_list)
            tempDF.rename(columns={field: key}, inplace=True)
            if metaDF.empty:
                metaDF = tempDF
            else:
                tempDF.drop('sample_name', axis=1, inplace=True)
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

    return metaDF


def quantAlphaMetaDF(qs1, metaDict):
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
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

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
            else:
                metaDF = metaDF.merge(tempDF, on='sampleid', how='outer')

    return metaDF


def normalizeAlpha(df, taxaDict, mySet, factor):
    df2 = df.reset_index()
    taxaID = ['kingdomid', 'phylaid', 'classid', 'orderid', 'familyid', 'genusid', 'speciesid']

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
            for x in xrange(reads):
                sub = np.random.mtrand.choice(range(sample.size), size=1, replace=True, p=prob)
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

    rowsList = []
    namesDF = pd.DataFrame()
    normDF = pd.DataFrame()
    for key in taxaDict:
        taxaList = taxaDict[key]

        if isinstance(taxaList, unicode):
            if key == 'Kingdom':
                qs1 = Kingdom.objects.filter(kingdomid=taxaList).values('kingdomid', 'kingdomName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['kingdomid', 'kingdomName'])
                namesDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomName': 'taxa_name'}, inplace=True)
            elif key == 'Phyla':
                qs1 = Phyla.objects.filter(phylaid=taxaList).values('phylaid', 'phylaName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['phylaid', 'phylaName'])
                namesDF.rename(columns={'phylaid': 'taxa_id', 'phylaName': 'taxa_name'}, inplace=True)
            elif key == 'Class':
                qs1 = Class.objects.filter(classid=taxaList).values('classid', 'className')
                namesDF = pd.DataFrame.from_records(qs1, columns=['classid', 'className'])
                namesDF.rename(columns={'classid': 'taxa_id', 'className': 'taxa_name'}, inplace=True)
            elif key == 'Order':
                qs1 = Order.objects.filter(orderid=taxaList).values('orderid', 'orderName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['orderid', 'orderName'])
                namesDF.rename(columns={'orderid': 'taxa_id', 'orderName': 'taxa_name'}, inplace=True)
            elif key == 'Family':
                qs1 = Family.objects.filter(familyid=taxaList).values('familyid', 'familyName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['familyid', 'familyName'])
                namesDF.rename(columns={'familyid': 'taxa_id', 'familyName': 'taxa_name'}, inplace=True)
            elif key == 'Genus':
                qs1 = Genus.objects.filter(genusid=taxaList).values('genusid', 'genusName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['genusid', 'genusName'])
                namesDF.rename(columns={'genusid': 'taxa_id', 'genusName': 'taxa_name'}, inplace=True)
            elif key == 'Species':
                qs1 = Species.objects.filter(speciesid=taxaList).values('speciesid', 'speciesName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['speciesid', 'speciesName'])
                namesDF.rename(columns={'speciesid': 'taxa_id', 'speciesName': 'taxa_name'}, inplace=True)
        else:
            if key == 'Kingdom':
                qs1 = Kingdom.objects.filter(kingdomid__in=taxaList).values('kingdomid', 'kingdomName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['kingdomid', 'kingdomName'])
                namesDF.rename(columns={'kingdomid': 'taxa_id', 'kingdomName': 'taxa_name'}, inplace=True)
            elif key == 'Phyla':
                qs1 = Phyla.objects.filter(phylaid__in=taxaList).values('phylaid', 'phylaName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['phylaid', 'phylaName'])
                namesDF.rename(columns={'phylaid': 'taxa_id', 'phylaName': 'taxa_name'}, inplace=True)
            elif key == 'Class':
                qs1 = Class.objects.filter(classid__in=taxaList).values('classid', 'className')
                namesDF = pd.DataFrame.from_records(qs1, columns=['classid', 'className'])
                namesDF.rename(columns={'classid': 'taxa_id', 'className': 'taxa_name'}, inplace=True)
            elif key == 'Order':
                qs1 = Order.objects.filter(orderid__in=taxaList).values('orderid', 'orderName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['orderid', 'orderName'])
                namesDF.rename(columns={'orderid': 'taxa_id', 'orderName': 'taxa_name'}, inplace=True)
            elif key == 'Family':
                qs1 = Family.objects.filter(familyid__in=taxaList).values('familyid', 'familyName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['familyid', 'familyName'])
                namesDF.rename(columns={'familyid': 'taxa_id', 'familyName': 'taxa_name'}, inplace=True)
            elif key == 'Genus':
                qs1 = Genus.objects.filter(genusid__in=taxaList).values('genusid', 'genusName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['genusid', 'genusName'])
                namesDF.rename(columns={'genusid': 'taxa_id', 'genusName': 'taxa_name'}, inplace=True)
            elif key == 'Species':
                qs1 = Species.objects.filter(speciesid__in=taxaList).values('speciesid', 'speciesName')
                namesDF = pd.DataFrame.from_records(qs1, columns=['speciesid', 'speciesName'])
                namesDF.rename(columns={'speciesid': 'taxa_id', 'speciesName': 'taxa_name'}, inplace=True)

        if key == 'Kingdom':
            rank = 'Kingdom'
            field = 'kingdomid'
        elif key == 'Phyla':
            rank = 'Phyla'
            field = 'phylaid'
        elif key == 'Class':
            rank = 'Class'
            field = 'classid'
        elif key == 'Order':
            rank = 'Order'
            field = 'orderid'
        elif key == 'Family':
            rank = 'Family'
            field = 'familyid'
        elif key == 'Genus':
            rank = 'Genus'
            field = 'genusid'
        elif key == 'Species':
            rank = 'Species'
            field = 'speciesid'

        for i in mySet:
            groupReads = countDF.groupby(field)[i].sum()
            groupAbund = relabundDF.groupby(field)[i].sum()
            groupRich = binaryDF.groupby(field)[i].sum()
            groupDiversity = diversityDF.groupby(field)[i].sum()
            if isinstance(taxaList, unicode):
                myDict = {}
                myDict['sampleid'] = i
                myDict['rank'] = rank
                myDict['taxa_id'] = taxaList
                myDict['count'] = groupReads[taxaList]
                myDict['total'] = groupReads.sum()
                myDict['rel_abund'] = groupAbund[taxaList]
                myDict['rich'] = groupRich[taxaList]
                myDict['diversity'] = groupDiversity[taxaList]
                rowsList.append(myDict)
            else:
                for j in taxaList:
                    myDict = {}
                    myDict['sampleid'] = i
                    myDict['rank'] = rank
                    myDict['taxa_id'] = j
                    myDict['count'] = groupReads[j]
                    myDict['total'] = groupReads.sum()
                    myDict['rel_abund'] = groupAbund[j]
                    myDict['rich'] = groupRich[j]
                    myDict['diversity'] = groupDiversity[j]
                    rowsList.append(myDict)
        DF1 = pd.DataFrame(rowsList, columns=['sampleid', 'rank', 'taxa_id', 'count', 'total', 'rel_abund', 'rich', 'diversity'])
        DF1 = DF1.merge(namesDF, on='taxa_id', how='outer')
        DF1 = DF1[['sampleid', 'rank', 'taxa_id', 'taxa_name', 'count', 'total', 'rel_abund', 'rich', 'diversity']]
        if normDF.empty:
            normDF = DF1
        else:
            normDF = normDF.append(DF1)
    return normDF
