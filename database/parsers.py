import time
import csv
import re
import math
from uuid import uuid4
from decimal import *
from models import Project, Sample, Collect, Climate, Soil_class, Soil_nutrient, Management, Microbial, User
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile
from models import ProfileKingdom, ProfilePhyla, ProfileClass, ProfileOrder, ProfileFamily, ProfileGenus, ProfileSpecies
from django.db.models import Sum, Count
import fileinput
from itertools import izip
import pandas as pd
from pandas.io.parsers import read_csv
from pandas import Series


def parse_project(filepath, uploaddate, Document, p_uuid):
    f = csv.DictReader(Document, delimiter=',')
    Document.close()
    for row in f:
        row_dict = row
        m = Project(projectid=p_uuid, path=filepath, upload_date=uploaddate, **row_dict)
        m.save()


def parse_sample(Document, p_uuid):
    f = csv.DictReader(Document, delimiter=',')
    Document.close()
    for row in f:
        s_uuid = uuid4().hex
        rowDict = row
        project = Project.objects.get(projectid=p_uuid)
        wanted_keys = ['sample_name', 'organism', 'title', 'seq_method', 'collection_date', 'biome', 'feature', 'geo_loc', 'lat_lon', 'material', 'elevation']
        sampleDict = {x: rowDict[x] for x in wanted_keys if x in rowDict}
        m = Sample(projectid=project, sampleid=s_uuid, **sampleDict)
        m.save()
        sample = Sample.objects.get(sampleid=s_uuid)

        wanted_keys = ['depth', 'pool_dna_extracts', 'samp_size', 'samp_collection_device', 'samp_weight_dna_ext', 'sieving', 'storage_cond']
        collectDict = {x: rowDict[x] for x in wanted_keys if x in rowDict}
        m = Collect(projectid=project, sampleid=sample, **collectDict)
        m.save()

        wanted_keys = ['annual_season_precpt', 'annual_season_temp']
        climateDict = {x: rowDict[x] for x in wanted_keys if x in rowDict}
        m = Climate(projectid=project, sampleid=sample, **climateDict)
        m.save()

        wanted_keys = ['bulk_density', 'drainage_class', 'fao_class', 'horizon', 'local_class', 'porosity', 'profile_position', 'slope_aspect', 'slope_gradient', 'soil_type', 'texture_class', 'water_content_soil']
        soil_classDict = {x: rowDict[x] for x in wanted_keys if x in rowDict}
        m = Soil_class(projectid=project, sampleid=sample, **soil_classDict)
        m.save()

        wanted_keys = ['pH', 'EC', 'tot_C', 'tot_OM', 'tot_N', 'NO3_N', 'NH4_N', 'P', 'K', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'Ca', 'Mg', 'Na', 'B']
        soil_nutrDict = {x: rowDict[x] for x in wanted_keys if x in rowDict}
        m = Soil_nutrient(projectid=project, sampleid=sample, **soil_nutrDict)
        m.save()

        wanted_keys = ['agrochem_addition', 'biological_amendment', 'cover_crop', 'crop_rotation', 'cur_land_use', 'cur_vegetation', 'cur_crop', 'cur_cultivar', 'organic', 'previous_land_use', 'soil_amendments', 'tillage']
        mgtDict = {x: rowDict[x] for x in wanted_keys if x in rowDict}
        m = Management(projectid=project, sampleid=sample, **mgtDict)
        m.save()

        wanted_keys = ['rRNA_copies', 'microbial_biomass_C', 'microbial_biomass_N', 'microbial_respiration']
        microbeDict = {x: rowDict[x] for x in wanted_keys if x in rowDict}
        m = Microbial(projectid=project, sampleid=sample, **microbeDict)
        m.save()

        wanted_keys = ['usr_cat1', 'usr_cat2', 'usr_cat3', 'usr_cat4', 'usr_cat5', 'usr_cat6', 'usr_quant1', 'usr_quant2', 'usr_quant3', 'usr_quant4', 'usr_quant5', 'usr_quant6']
        userDict = {x: rowDict[x] for x in wanted_keys if x in rowDict}
        m = User(projectid=project, sampleid=sample, **userDict)
        m.save()


def parse_taxonomy(Document):
    f = csv.reader(Document, delimiter='\t')
    f.next()

    for line in f:
        subbed = re.sub(r'\(.*?\)', '', line[2])
        taxon = subbed.split(';')

        if not Kingdom.objects.filter(kingdomName=taxon[0]).exists():
            id = uuid4().hex
            record = Kingdom(kingdomid=id, kingdomName=taxon[0])
            record.save()
        k = Kingdom.objects.get(kingdomName=taxon[0]).kingdomid

        if not Phyla.objects.filter(kingdomid_id=k, phylaName=taxon[1]).exists():
            id = uuid4().hex
            record = Phyla(kingdomid_id=k, phylaid=id, phylaName=taxon[1])
            record.save()
        p = Phyla.objects.get(kingdomid_id=k, phylaName=taxon[1]).phylaid

        if not Class.objects.filter(kingdomid_id=k, phylaid_id=p, className=taxon[2]).exists():
            id = uuid4().hex
            record = Class(kingdomid_id=k, phylaid_id=p, classid=id, className=taxon[2])
            record.save()
        c = Class.objects.get(kingdomid_id=k, phylaid_id=p, className=taxon[2]).classid

        if not Order.objects.filter(kingdomid_id=k, phylaid_id=p, classid_id=c, orderName=taxon[3]).exists():
            id = uuid4().hex
            record = Order(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid=id, orderName=taxon[3])
            record.save()
        o = Order.objects.get(kingdomid_id=k, phylaid_id=p, classid_id=c, orderName=taxon[3]).orderid

        if not Family.objects.filter(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid_id=o, familyName=taxon[4]).exists():
            id = uuid4().hex
            record = Family(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid_id=o, familyid=id, familyName=taxon[4])
            record.save()
        f = Family.objects.get(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid_id=o, familyName=taxon[4]).familyid

        if not Genus.objects.filter(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid_id=o, familyid_id=f, genusName=taxon[5]).exists():
            id = uuid4().hex
            record = Genus(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid_id=o, familyid_id=f, genusid=id, genusName=taxon[5])
            record.save()
        g = Genus.objects.get(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid_id=o, familyid_id=f, genusName=taxon[5]).genusid

        if not Species.objects.filter(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid_id=o, familyid_id=f, genusid_id=g, speciesName=taxon[6]).exists():
            id = uuid4().hex
            record = Species(kingdomid_id=k, phylaid_id=p, classid_id=c, orderid_id=o, familyid_id=f, genusid_id=g, speciesid=id, speciesName=taxon[6])
            record.save()


def parse_profile(path, p_uuid):
    file1 = str(path) + '/mothur.taxonomy'
    df1 = pd.io.parsers.read_csv(file1, sep='\t', header=0, index_col='OTU')
    df1.drop('Size', axis=1, inplace=True)

    file2 = str(path) + '/mothur.shared'
    df2 = pd.io.parsers.read_csv(file2, sep='\t', header=0, index_col='Group')
    df2.drop(['label', 'numOtus'], axis=1, inplace=True)
    df3 = df2.T

    df4 = df1.merge(df3, left_index=True, right_index=True, how='outer')

    df4['Taxonomy'].replace(to_replace='\(.*?\)', value='', regex=True, inplace=True)
    df4.reset_index(inplace=True)

    df4.drop(['OTU'], axis=1, inplace=True)
    df4.set_index(['Taxonomy'], inplace=True)
    df5 = df4.unstack().reset_index(name='count')
    df5.rename(columns={'level_0': 'sample'}, inplace=True)

    df6 = df5.groupby('sample')['count'].sum().reset_index()
    df6.rename(columns={'count': 'total'}, inplace=True)
    df7 = df5.merge(df6, on='sample', how='outer')
    df7['rel_abund'] = df7['count'] / df7['total']
    df7['binary'] = df7['count'].apply(lambda x: 1 if x > 0 else 0)
    df7['diversity'] = df7['rel_abund'].apply(lambda x: -1 * x * math.log(x) if x > 0 else 0)

    df8 = df7['Taxonomy'].str.split(';').apply(Series, 1)
    df8.rename(columns={0: 'kingdom', 1: 'phyla', 2: 'class', 3: 'order', 4: 'family', 5: 'genus', 6: 'species'}, inplace=True)
    df9 = df7.join(df8, how='outer')

    for index, row in df9.iterrows():
        if row['count'] > 0:
            name = row['sample']
            k = row['kingdom']
            p =  row['phyla']
            c = row['class']
            o = row['order']
            f = row['family']
            g = row['genus']
            s = row['species']
            count = row['count']
            total = row['total']
            rel_abund = row['rel_abund']
            binary = row['binary']
            diversity = row['diversity']
            project = Project.objects.get(projectid=p_uuid)
            sample = Sample.objects.filter(projectid=p_uuid).get(sample_name=name)
            t_kingdom = Kingdom.objects.get(kingdomName=k)
            t_phyla = Phyla.objects.get(kingdomid_id=t_kingdom, phylaName=p)
            t_class = Class.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, className=c)
            t_order = Order.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, classid_id=t_class, orderName=o)
            t_family = Family.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, classid_id=t_class, orderid_id=t_order, familyName=f)
            t_genus = Genus.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, classid_id=t_class, orderid_id=t_order, familyid_id=t_family, genusName=g)
            t_species = Species.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, classid_id=t_class, orderid_id=t_order, familyid_id=t_family, genusid_id=t_genus, speciesName=s)
            record = Profile(projectid=project, sampleid=sample, kingdomid=t_kingdom, phylaid=t_phyla, classid=t_class, orderid=t_order, familyid=t_family, genusid=t_genus, speciesid=t_species, count=count, total=total, rel_abund=rel_abund, binary=binary, diversity=diversity)
            record.save()


def taxaprofile(p_uuid):
    getcontext().prec = 6
    project = Project.objects.get(projectid=p_uuid)

    q1 = Profile.objects.filter(projectid_id=project)

    dict = q1.values('kingdomid', 'sampleid').annotate(count=Sum('count'), rel_abund=Sum('rel_abund'), rich=Sum('binary'), diversity=Sum('diversity'))
    for myDict in dict:
        s_uuid = myDict['sampleid']
        del myDict['sampleid']
        sample = Sample.objects.get(sampleid=s_uuid)
        k_uuid = myDict['kingdomid']
        kingdom = Kingdom.objects.get(kingdomid=k_uuid)
        del myDict['kingdomid']
        m = ProfileKingdom(projectid=project, sampleid=sample, kingdomid=kingdom, **myDict)
        m.save()

    dict = q1.values('phylaid', 'sampleid').annotate(count=Sum('count'), rel_abund=Sum('rel_abund'), rich=Sum('binary'), diversity=Sum('diversity'))
    for myDict in dict:
        s_uuid = myDict['sampleid']
        del myDict['sampleid']
        sample = Sample.objects.get(sampleid=s_uuid)
        p_uuid = myDict['phylaid']
        phyla = Phyla.objects.get(phylaid=p_uuid)
        del myDict['phylaid']
        m = ProfilePhyla(projectid=project, sampleid=sample, phylaid=phyla, **myDict)
        m.save()

    dict = q1.values('classid', 'sampleid').annotate(count=Sum('count'), rel_abund=Sum('rel_abund'), rich=Sum('binary'), diversity=Sum('diversity'))
    for myDict in dict:
        s_uuid = myDict['sampleid']
        del myDict['sampleid']
        sample = Sample.objects.get(sampleid=s_uuid)
        c_uuid = myDict['classid']
        classes = Class.objects.get(classid=c_uuid)
        del myDict['classid']
        m = ProfileClass(projectid=project, sampleid=sample, classid=classes, **myDict)
        m.save()

    dict = q1.values('orderid', 'sampleid').annotate(count=Sum('count'), rel_abund=Sum('rel_abund'), rich=Sum('binary'), diversity=Sum('diversity'))
    for myDict in dict:
        s_uuid = myDict['sampleid']
        del myDict['sampleid']
        sample = Sample.objects.get(sampleid=s_uuid)
        o_uuid = myDict['orderid']
        order = Order.objects.get(orderid=o_uuid)
        del myDict['orderid']
        m = ProfileOrder(projectid=project, sampleid=sample, orderid=order, **myDict)
        m.save()

    dict = q1.values('familyid', 'sampleid').annotate(count=Sum('count'), rel_abund=Sum('rel_abund'), rich=Sum('binary'), diversity=Sum('diversity'))
    for myDict in dict:
        s_uuid = myDict['sampleid']
        del myDict['sampleid']
        sample = Sample.objects.get(sampleid=s_uuid)
        f_uuid = myDict['familyid']
        family = Family.objects.get(familyid=f_uuid)
        del myDict['familyid']
        m = ProfileFamily(projectid=project, sampleid=sample, familyid=family, **myDict)
        m.save()

    dict = q1.values('genusid', 'sampleid').annotate(count=Sum('count'), rel_abund=Sum('rel_abund'), rich=Sum('binary'), diversity=Sum('diversity'))
    for myDict in dict:
        s_uuid = myDict['sampleid']
        del myDict['sampleid']
        sample = Sample.objects.get(sampleid=s_uuid)
        g_uuid = myDict['genusid']
        genus = Genus.objects.get(genusid=g_uuid)
        del myDict['genusid']
        m = ProfileGenus(projectid=project, sampleid=sample, genusid=genus, **myDict)
        m.save()

    dict = q1.values('speciesid', 'sampleid').annotate(count=Sum('count'), rel_abund=Sum('rel_abund'), rich=Sum('binary'), diversity=Sum('diversity'))
    for myDict in dict:
        s_uuid = myDict['sampleid']
        del myDict['sampleid']
        sample = Sample.objects.get(sampleid=s_uuid)
        s_uuid = myDict['speciesid']
        species = Species.objects.get(speciesid=s_uuid)
        del myDict['speciesid']
        m = ProfileSpecies(projectid=project, sampleid=sample, speciesid=species, **myDict)
        m.save()
