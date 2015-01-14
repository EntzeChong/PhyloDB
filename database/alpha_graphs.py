from alpha_dataframe import catAlphaMetaDF, quantAlphaMetaDF, normalizeAlpha
from django.http import HttpResponse
from models import Sample
from models import Kingdom, Phyla, Profile
import numpy as np      ### pycharm doesn't recognize, but this is required
from numpy import *
import pandas as pd
import pickle
from pyvttbl import Anova1way
from scipy import stats
import simplejson
from utils import multidict, taxaProfileDF


def getCatAlphaData(request):
    ### get sample list from cookie
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
        selectAll = int(all["selectAll"])

        metaString = all["meta"]

        ### function to merge values on common keys
        metaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(metaString)

        ### function to create a meta variable DataFrame
        metaDF = catAlphaMetaDF(qs1, metaDict)

        myList = metaDF['sampleid'].tolist()
        mySet = list(set(myList))

        ### function to create a taxa DataFrame
        taxaDF = taxaProfileDF(mySet)

        ### function to merge values on common keys
        taxaString = all["taxa"]
        ### this taxaDict is from the dynatree (ajax call)
        taxaDict = simplejson.JSONDecoder(object_pairs_hook=multidict).decode(taxaString)

        # change dict if selectAll levels is on (avoids loading entire tree first)
        if selectAll == 1:
            taxaDict = {}
            qs1 = Profile.objects.all().filter(sampleid__in=mySet).values_list('kingdomid', flat='True').distinct()
            taxaDict['Kingdom'] = qs1
        elif selectAll == 2:
            taxaDict = {}
            qs1 = Profile.objects.all().filter(sampleid__in=mySet).values_list('phylaid', flat='True').distinct()
            taxaDict['Phyla'] = qs1
        elif selectAll == 3:
            taxaDict = {}
            qs1 = Profile.objects.all().filter(sampleid__in=mySet).values_list('classid', flat='True').distinct()
            taxaDict['Class'] = qs1
        elif selectAll == 4:
            taxaDict = {}
            qs1 = Profile.objects.all().filter(sampleid__in=mySet).values_list('orderid', flat='True').distinct()
            taxaDict['Order'] = qs1
        elif selectAll == 5:
            taxaDict = {}
            qs1 = Profile.objects.all().filter(sampleid__in=mySet).values_list('familyid', flat='True').distinct()
            taxaDict['Family'] = qs1
        elif selectAll == 6:
            taxaDict = {}
            qs1 = Profile.objects.all().filter(sampleid__in=mySet).values_list('genusid', flat='True').distinct()
            taxaDict['Genus'] = qs1
        elif selectAll == 7:
            taxaDict = {}
            qs1 = Profile.objects.all().filter(sampleid__in=mySet).values_list('speciesid', flat='True').distinct()
            taxaDict['Species'] = qs1

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

        ### function to normalize the number of sequence reads per sample
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

        ### group DataFrame by each taxa level selected
        grouped1 = finalDF.groupby(['rank', 'taxa_name', 'taxa_id'])
        equal_error = 'no'

        ### group DataFrame by each meta variable selected
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
                ### for taxa with only 1 species all values will be '1' and cause an anova error
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

            ### One-way ANOVA with some error checking
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

            ### select only significant ANOVAs for output (graph & text area)
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
                    seriesDict['name'] = name1
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

            ### select all ANOVAs for output (graph & text area)
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
                seriesDict['name'] = name1
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

        finalDF.reset_index(drop=True, inplace=True)
        res_table = finalDF.to_html(classes="table display")
        res_table = res_table.replace('border="1"', 'border="0"')
        finalDict['res_table'] = str(res_table)

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
        metaDF = quantAlphaMetaDF(qs1, metaDict)

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

        final_fieldList = []
        for key in metaDict:
            final_fieldList.append(metaDict[key])

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
                seriesDict['name'] = name1
                seriesDict['data'] = dataList
                seriesList.append(seriesDict)
                if stop == 0:
                    regDict = {}
                elif stop == 1:
                    regrDict = {}
                    regrDict['type'] = 'line'
                    name2 = list(name1)
                    temp = 'R2: ' + str(r_square) + '; p-value: ' + str(p_value) + '<br>' + '(y = ' + str(slope) + 'x' + ' + ' + str(intercept)
                    print temp
                    name2.append(temp)
                    print name2
                    regrDict['name'] = name2
                    regrDict['data'] = regrList
                    seriesList.append(regrDict)

            if sig_only == 1:
                if p_value <= 0.05:
                    seriesDict = {}
                    seriesDict['type'] = 'scatter'
                    name2 = list(name1)
                    temp = 'R2: ' + str(r_square) + '; p-value: ' + str(p_value) + '<br>' + '(y = ' + str(slope) + 'x' + ' + ' + str(intercept)
                    name2.append(temp)
                    seriesDict['name'] = name2
                    seriesDict['data'] = dataList
                    seriesList.append(seriesDict)

                    regrDict = {}
                    regrDict['type'] = 'line'
                    regrDict['name'] = name1
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

        finalDF.reset_index(drop=True, inplace=True)
        res_table = finalDF.to_html(classes="table display")
        res_table = res_table.replace('border="1"', 'border="0"')
        finalDict['res_table'] = str(res_table)

        res = simplejson.dumps(finalDict)
        return HttpResponse(res, content_type='application/json')


