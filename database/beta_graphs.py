from beta_dataframe import catBetaMetaDF, quantBetaMetaDF, normalizeBeta
from django.http import HttpResponse
from models import Sample
import numpy as np      ### pycharm doesn't recognize, but this is required
from numpy import *
import pandas as pd
import pickle
from scipy import stats
from scipy.spatial.distance import *
import simplejson
from utils import multidict, taxaProfileDF, permanova_oneway, PCoA


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
        if norm == 1:
            factor = 'none'
        elif norm == 2:
            factor = 'min'
        elif norm == 3:
            factor = '10th percentile'
        elif norm == 4:
            factor = '25th percentile'
        elif norm == 5:
            factor = 'median'

        normDF = normalizeBeta(taxaDF, taxaLevel, mySet, factor)

        finalDF = metaDF.merge(normDF, on='sampleid', how='outer')
        pd.set_option('display.max_rows', finalDF.shape[0], 'display.max_columns', finalDF.shape[1], 'display.width', 1000)

        fieldList = []
        for key in metaDict:
            fieldList.append(key)

        matrixDF = pd.DataFrame()
        if button == 1:
            matrixDF = finalDF.pivot(index='taxaid', columns='sampleid', values='count')
        elif button == 2:
            matrixDF = finalDF.pivot(index='taxaid', columns='sampleid', values='rel_abund')
        elif button == 3:
            matrixDF = finalDF.pivot(index='taxaid', columns='sampleid', values='rich')
        elif button == 4:
            matrixDF = finalDF.pivot(index='taxaid', columns='sampleid', values='diversity')

        datamtx = asarray(matrixDF[mySet].T)
        numrows, numcols = shape(datamtx)
        dists = np.zeros((numrows, numrows))

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
        pcoaDF = pd.DataFrame(coordinates, columns=axesList, index=mySet)
        resultDF = metaDF.join(pcoaDF)
        pd.set_option('display.max_rows', resultDF.shape[0], 'display.max_columns', resultDF.shape[1], 'display.width', 1000)

        ### create trtList that merges all categorical values
        groupList = metaDF[fieldList].values.tolist()
        trtList = []
        for i in groupList:
            trtList.append(':'.join(i))

        ### check to see if all samples are the same size
        sizeList = []
        grouped = resultDF.groupby(fieldList)
        for name, group in grouped:
            (row, col) = shape(group)
            sizeList.append(row)
        setSize = len(set(sizeList))

        if setSize == 1:
            try:
                bigf, p = permanova_oneway(dists, trtList, 200)
            except:
                bigf = float('nan')
                p = float('nan')
        else:
            bigf = float('nan')
            p = float('nan')

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
            result = result + 'The current version requires all treatments to be of equal sample size.' + '\n'
        else:
            result = result + '===============================================\n'
            result = result + 'perMANOVA results' + '\n'
            result = result + 'f-value: ' + str(bigf) + '\n'
            result = result + 'p-value: ' + str(p) + '\n'

        result = result + '===============================================\n'
        result = result + str(eigenDF) + '\n'
        result = result + '===============================================\n'
        result = result + '\n\n\n\n'

        finalDict['text'] = result

        resultDF.reset_index(drop=True, inplace=True)
        res_table = resultDF.to_html(classes="table display")
        res_table = res_table.replace('border="1"', 'border="0"')
        finalDict['res_table'] = str(res_table)

        nameList = list(metaDF['sample_name'])
        distsDF = pd.DataFrame(dists, columns=nameList, index=nameList)
        dist_table = distsDF.to_html(classes="table display")
        dist_table = dist_table.replace('border="1"', 'border="0"')
        finalDict['dist_table'] = str(dist_table)

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
        if norm == 1:
            factor = 'none'
        elif norm == 2:
            factor = 'min'
        elif norm == 3:
            factor = '10th percentile'
        elif norm == 4:
            factor = '25th percentile'
        elif norm == 5:
            factor = 'median'

        normDF = normalizeBeta(taxaDF, taxaLevel, mySet, factor)

        finalDF = metaDF.merge(normDF, on='sampleid', how='outer')
        pd.set_option('display.max_rows', finalDF.shape[0], 'display.max_columns', finalDF.shape[1], 'display.width', 1000)

        fieldList = []
        for key in metaDict:
            fieldList.append(metaDict[key])

        matrixDF = pd.DataFrame()
        if button == 1:
            matrixDF = finalDF.pivot(index='taxaid', columns='sampleid', values='count')
        elif button == 2:
            matrixDF = finalDF.pivot(index='taxaid', columns='sampleid', values='rel_abund')
        elif button == 3:
            matrixDF = finalDF.pivot(index='taxaid', columns='sampleid', values='rich')
        elif button == 4:
            matrixDF = finalDF.pivot(index='taxaid', columns='sampleid', values='diversity')

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
        pcoaDF = pd.DataFrame(coordinates, columns=axesList, index=mySet)
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
        result = result + '\n\n\n\n'

        finalDict['text'] = result

        resultDF.reset_index(drop=True, inplace=True)
        res_table = resultDF.to_html(classes="table display")
        res_table = res_table.replace('border="1"', 'border="0"')
        finalDict['res_table'] = str(res_table)

        nameList = list(metaDF['sample_name'])
        distsDF = pd.DataFrame(dists, columns=nameList, index=nameList)
        dist_table = distsDF.to_html(classes="table display")
        dist_table = dist_table.replace('border="1"', 'border="0"')
        finalDict['dist_table'] = str(dist_table)

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')


