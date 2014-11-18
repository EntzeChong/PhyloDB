import csv
import re
from uuid import uuid4
from models import Project, Sample, Collect, Climate, Soil_class, Soil_nutrient, Management, Microbial, User
from models import Kingdom, Phyla, Class, Order, Family, Genus, Species, Profile

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
        row_dict = row
        project = Project.objects.get(projectid=p_uuid)
        m = Sample(projectid=project, sampleid=s_uuid, **row_dict)
        m.save()
        sample = Sample.objects.get(sampleid=s_uuid)
        m = Collect(projectid=project, sampleid=sample, **row_dict)
        m.save()
        m = Collect(projectid=project, sampleid=sample, **row_dict)
        m.save()
        m = Climate(projectid=project, sampleid=sample, **row_dict)
        m.save()
        m = Soil_class(projectid=project, sampleid=sample, **row_dict)
        m.save()
        m = Soil_nutrient(projectid=project, sampleid=sample, **row_dict)
        m.save()
        m = Management(projectid=project, sampleid=sample, **row_dict)
        m.save()
        m = Microbial(projectid=project, sampleid=sample, **row_dict)
        m.save()
        m = User(projectid=project, sampleid=sample, **row_dict)
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
    samples = Sample.objects.all().filter(projectid_id=p_uuid)
    kingdoms = Kingdom.objects.get('kingdomid').distinct()
    #phylas = Phyla.objects.get('phylaid').distinct()
    #class = Class.objects.get('phylaid').distinct()
    #order = Order.objects.get('phylaid').distinct()
    #family = Family.objects.get('phylaid').distinct()
    #genus = Genus.objects.get('phylaid').distinct()
    #species = Species.objects.get('phylaid').distinct()

    for kingdom in kingdoms:
        for sample in samples:
            count = Profile.objects.aggregate('count').filter(sampleid_id=sample.sampleid).filter(kingdomid_id=kingdom.kingdomid)
            print count
            #create Dict
            #save