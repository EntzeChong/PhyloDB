import pandas as pd
from scipy.spatial.distance import *
import numpy as np
from numpy import asarray, shape, zeros
import random as r
from itertools import permutations, product, chain
from scipy import stats
from utils import principalComponents, permanova_oneway


df = pd.DataFrame({'Sample1': [0, 2, 4, 6, 8, 10], 'Sample2': [0, 2, 4, 6, 8, 10], 'Sample3': [10, 8, 6, 4, 2, 0], 'Sample4': [1, 2, 3, 4, 5, 6], 'Sample5': [3, 6, 7, 2, 4, 0], 'Sample6': [0, 8, 6, 4, 2, 1]}, index=['OTU1', 'OTU2', 'OTU3', 'OTU4', 'OTU5', 'OTU6'])
print 'df\n', df, '\n'

sampleList = list(df.columns.values)

sampleDF = pd.DataFrame({'group': [1, 1, 1, 2, 2, 2]}, index=sampleList)
print 'sampleDF\n', sampleDF, '\n'

## Calculate distance matrix
datamtx = asarray(df.T)
numrows, numcols = shape(datamtx)
dists = zeros((numrows, numrows))

for x in range(numrows):
    for y in range(1, numrows):
        try:
            dist = braycurtis(datamtx[x], datamtx[y])
            dists[x, y] = dists[y, x] = dist
        except:
            dist = 0
            dists[x, y] = dists[y, x] = dist

distDF = pd.DataFrame(dists, columns=sampleList, index=sampleList)
print 'distDF\n', distDF, '\n'

pcoa = principalComponents(dists)
numaxes = len(pcoa[0])
axesList = []
for i in range(len(pcoa[0])):
    j = i + 1
    axesList.append('PC' + str(j))

eigenDF = pd.DataFrame(pcoa[0], columns=['EigenVectors'], index=axesList)
pcoaDF = pd.DataFrame(pcoa[1], columns=axesList, index=sampleList)

print 'eigenvalues\n', eigenDF, '\n'
print 'principal components\n', pcoaDF, '\n'


