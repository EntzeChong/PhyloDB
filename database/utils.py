import pandas as pd
import numpy as np      ### pycharm doesn't recognize, but this is required
from numpy import *
import os
import shutil
from collections import defaultdict
from models import Project, Profile
from scipy.spatial.distance import *
from scipy import stats
import random as r
from itertools import product


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


def taxaProfileDF(mySet):
    qs1 = Profile.objects.filter(sampleid__in=mySet).values('sampleid', 'kingdomid', 'phylaid', 'classid', 'orderid', 'familyid', 'genusid', 'speciesid', 'count')
    df = pd.DataFrame.from_records(qs1, columns=['sampleid', 'kingdomid', 'phylaid', 'classid', 'orderid', 'familyid', 'genusid', 'speciesid', 'count'])
    df.set_index(['sampleid', 'kingdomid', 'phylaid', 'classid', 'orderid', 'familyid', 'genusid', 'speciesid'], drop=True, inplace=True)
    df2 = df.unstack(['sampleid']).fillna(0).stack(['sampleid'])
    df3 = df2.unstack(['sampleid'])
    taxaDF = df3['count']
    return taxaDF


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


def permanova_oneway(dm, levels, permutations=1000):
    bigf = f_oneway(dm, levels)
    above = below = 0
    nf = 0
    shuffledlevels = list(levels)
    for i in xrange(permutations):
        r.shuffle(shuffledlevels)
        f = f_oneway(dm, shuffledlevels)
        if f >= bigf:
            above += 1
    p = above/float(permutations)
    return bigf, p


def f_oneway(dm, levels):
    bign = len(levels)
    dm = np.asarray(dm)
    a = len(set(levels))
    n = bign/a
    assert dm.shape == (bign, bign)
    sst = np.sum(stats.ss(r) for r in (s[n+1:] for n, s in enumerate(dm[:-1])))/float(bign)
    ssw = np.sum((dm[i][j]**2 for i, j in product(xrange(len(dm)), xrange(1, len(dm))) if i < j and levels[i] == levels[j]))/float(n)
    ssa = sst - ssw
    fstat = (ssa/float(a-1))/(ssw/float(bign-a))
    return fstat


def PCoA(dm):
    E_matrix = make_E_matrix(dm)
    F_matrix = make_F_matrix(E_matrix)
    eigvals, eigvecs = np.linalg.eigh(F_matrix)
    negative_close_to_zero = np.isclose(eigvals, 0)
    eigvals[negative_close_to_zero] = 0
    idxs_descending = eigvals.argsort()[::-1]
    eigvals = eigvals[idxs_descending]
    eigvecs = eigvecs[:, idxs_descending]
    eigvals, coordinates, proportion_explained = scores(eigvals, eigvecs)
    return eigvals, coordinates, proportion_explained


def make_E_matrix(dist_matrix):
    return (dist_matrix * dist_matrix) / -2.0


def make_F_matrix(E_matrix):
    col_means = E_matrix.mean(axis=1, keepdims=True, dtype=np.float64)
    row_means = E_matrix.mean(axis=0, keepdims=True, dtype=np.float64)
    matrix_mean = E_matrix.mean(dtype=np.float64)
    return E_matrix - row_means - col_means + matrix_mean


def scores(eigvals, eigvecs):
    num_positive = (eigvals >= 0).sum()
    eigvecs[:, num_positive:] = np.zeros(eigvecs[:, num_positive:].shape)
    eigvals[num_positive:] = np.zeros(eigvals[num_positive:].shape)
    coordinates = eigvecs * np.sqrt(eigvals)
    proportion_explained = eigvals / eigvals.sum()
    return eigvals, coordinates, proportion_explained

