import csv
import re
from uuid import uuid4
from models import Project, Sample, Collect, Climate, Soil_class, Soil_nutrient, Management, Microbial, User
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile
from models import ProfileKingdom, ProfilePhyla, ProfileClass, ProfileOrder, ProfileFamily, ProfileGenus, ProfileSpecies
from django.db.models import Sum

import fileinput
from itertools import izip

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

        wanted_keys = ['pH', 'EC', 'tot_C', 'tot_OM', 'tot_N', 'NO3_N', 'NH4_mN', 'P', 'K', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'Ca', 'Mg', 'Na', 'B']
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


def parse_profile(taxonomy, shared, path, p_uuid):
    f = csv.reader(taxonomy, delimiter='\t')
    taxonomy.close()
    f.next()
    taxa_list = []
    for line in f:
        subbed = re.sub(r'\(.*?\)', '', line[2])
        taxa_list.append(subbed)

    f = izip(*csv.reader(shared, delimiter='\t'))
    shared.close()
    outfile = "/".join([path, "shared.tr"])
    csv.writer(open(outfile, 'wb'), delimiter='\t').writerows(f)

    for line in fileinput.input(outfile, inplace=True):
        line = line.rstrip()
        if fileinput.lineno() == 1 or fileinput.lineno() == 3:
            continue
        print line
    samples_list = {}

    j = 0
    for line in fileinput.input(outfile):
        if line.strip():
            if fileinput.lineno() == 1:
                line = line.rstrip()
                samples_list = line.split('\t')
                samples_list.pop(0)
            else:
                row = line.split('\t')
                for i in range(len(samples_list)):
                    count = int(row[i+1])
                    if count != 0:
                        taxon = taxa_list[j].split(';')
                        name = samples_list[i]
                        project = Project.objects.get(projectid=p_uuid)
                        sample = Sample.objects.filter(projectid=p_uuid).get(sample_name=name)
                        t_kingdom = Kingdom.objects.get(kingdomName=taxon[0])
                        t_phyla = Phyla.objects.get(kingdomid_id=t_kingdom, phylaName=taxon[1])
                        t_class = Class.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, className=taxon[2])
                        t_order = Order.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, classid_id=t_class, orderName=taxon[3])
                        t_family = Family.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, classid_id=t_class, orderid_id=t_order, familyName=taxon[4])
                        t_genus = Genus.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, classid_id=t_class, orderid_id=t_order, familyid_id=t_family, genusName=taxon[5])
                        t_species = Species.objects.get(kingdomid_id=t_kingdom, phylaid_id=t_phyla, classid_id=t_class, orderid_id=t_order, familyid_id=t_family, genusid_id=t_genus, speciesName=taxon[6])
                        record = Profile(projectid=project, sampleid=sample, kingdomid=t_kingdom, phylaid=t_phyla, classid=t_class, orderid=t_order, familyid=t_family, genusid=t_genus, speciesid=t_species, count=count)
                        record.save()
                j += 1

def taxaprofile(p_uuid):
    project = Project.objects.get(projectid=p_uuid)
    sample_list = Sample.objects.values_list('sampleid')

    for item in sample_list:
        count = Profile.objects.filter(sampleid=item).values('kingdomid').annotate(sum=Sum('count'))
        for i in count:
            myDict = i
            myDict['count'] = myDict.pop('sum')
            sample = Sample.objects.get(sampleid=item)
            k_uuid = myDict['kingdomid']
            kingdom = Kingdom.objects.get(kingdomid=k_uuid)
            del myDict['kingdomid']
            m = ProfileKingdom(projectid=project, sampleid=sample, kingdomid=kingdom, **myDict)
            m.save()

        count = Profile.objects.filter(sampleid=item).values('phylaid').annotate(sum=Sum('count'))
        for i in count:
            myDict = i
            myDict['count'] = myDict.pop('sum')
            sample = Sample.objects.get(sampleid=item)
            p_uuid = myDict['phylaid']
            phyla = Phyla.objects.get(phylaid=p_uuid)
            del myDict['phylaid']
            m = ProfilePhyla(projectid=project, sampleid=sample, phylaid=phyla, **myDict)
            m.save()

        count = Profile.objects.filter(sampleid=item).values('classid').annotate(sum=Sum('count'))
        for i in count:
            myDict = i
            myDict['count'] = myDict.pop('sum')
            sample = Sample.objects.get(sampleid=item)
            c_uuid = myDict['classid']
            tclass = Class.objects.get(classid=c_uuid)
            del myDict['classid']
            m = ProfileClass(projectid=project, sampleid=sample, classid=tclass, **myDict)
            m.save()

        count = Profile.objects.filter(sampleid=item).values('orderid').annotate(sum=Sum('count'))
        for i in count:
            myDict = i
            myDict['count'] = myDict.pop('sum')
            sample = Sample.objects.get(sampleid=item)
            o_uuid = myDict['orderid']
            order = Order.objects.get(orderid=o_uuid)
            del myDict['orderid']
            m = ProfileOrder(projectid=project, sampleid=sample, orderid=order, **myDict)
            m.save()

        count = Profile.objects.filter(sampleid=item).values('familyid').annotate(sum=Sum('count'))
        for i in count:
            myDict = i
            myDict['count'] = myDict.pop('sum')
            sample = Sample.objects.get(sampleid=item)
            f_uuid = myDict['familyid']
            family = Family.objects.get(familyid=f_uuid)
            del myDict['familyid']
            m = ProfileFamily(projectid=project, sampleid=sample, familyid=family, **myDict)
            m.save()

        count = Profile.objects.filter(sampleid=item).values('genusid').annotate(sum=Sum('count'))
        for i in count:
            myDict = i
            myDict['count'] = myDict.pop('sum')
            sample = Sample.objects.get(sampleid=item)
            g_uuid = myDict['genusid']
            genus = Genus.objects.get(genusid=g_uuid)
            del myDict['genusid']
            m = ProfileGenus(projectid=project, sampleid=sample, genusid=genus, **myDict)
            m.save()

        count = Profile.objects.filter(sampleid=item).values('speciesid').annotate(sum=Sum('count'))
        for i in count:
            myDict = i
            myDict['count'] = myDict.pop('sum')
            sample = Sample.objects.get(sampleid=item)
            sp_uuid = myDict['speciesid']
            species = Species.objects.get(speciesid=sp_uuid)
            del myDict['speciesid']
            m = ProfileSpecies(projectid=project, sampleid=sample, speciesid=species, **myDict)
            m.save()
