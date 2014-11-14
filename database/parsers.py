import csv
import re
from uuid import uuid4
from models import Project, Sample, Kingdom, Phyla, Class, Order, Family, Genus, Species

import fileinput
from itertools import izip

def parse_project(filepath, uploaddate, Document, p_uuid):
    f = csv.DictReader(Document, delimiter=',')
    for row in f:
        row_dict = row
        m = Project(projectid=p_uuid, path=filepath, upload_date=uploaddate, **row_dict)
        m.save()


def parse_sample(Document, p_uuid):
    f = csv.DictReader(Document, delimiter=',')
    for row in f:
        s_uuid = uuid4().hex
        row_dict = row
        project = Project.objects.get(projectid=p_uuid)
        m = Sample(projectid=project, sampleid=s_uuid, **row_dict)
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

        if not Phyla.objects.filter(phylaName=taxon[1]).exists():
            id2 = uuid4().hex
            id1 = Kingdom.objects.get(kingdomName=taxon[0])
            record = Phyla(kingdomid=id1, phylaid=id2, phylaName=taxon[1])
            record.save()

        if not Class.objects.filter(className=taxon[2]).exists():
            id3 = uuid4().hex
            id2 = Phyla.objects.get(phylaName=taxon[1])
            id1 = Kingdom.objects.get(kingdomName=taxon[0])
            record = Class(kingdomid=id1, phylaid=id2, classid=id3, className=taxon[2])
            record.save()

        if not Order.objects.filter(orderName=taxon[3]).exists():
            id4 = uuid4().hex
            id3 = Class.objects.get(className=taxon[2])
            id2 = Phyla.objects.get(phylaName=taxon[1])
            id1 = Kingdom.objects.get(kingdomName=taxon[0])
            record = Order(kingdomid=id1, phylaid=id2, classid=id3, orderid=id4, orderName=taxon[3])
            record.save()

        if not Family.objects.filter(familyName=taxon[4]).exists():
            id5 = uuid4().hex
            id4 = Order.objects.get(orderName=taxon[3])
            id3 = Class.objects.get(className=taxon[2])
            id2 = Phyla.objects.get(phylaName=taxon[1])
            id1 = Kingdom.objects.get(kingdomName=taxon[0])
            record = Family(kingdomid=id1, phylaid=id2, classid=id3, orderid=id4, familyid=id5, familyName=taxon[4])
            record.save()

        if not Genus.objects.filter(genusName=taxon[5]).exists():
            id6 = uuid4().hex
            id5 = Family.objects.get(familyName=taxon[4])
            id4 = Order.objects.get(orderName=taxon[3])
            id3 = Class.objects.get(className=taxon[2])
            id2 = Phyla.objects.get(phylaName=taxon[1])
            id1 = Kingdom.objects.get(kingdomName=taxon[0])
            record = Genus(kingdomid=id1, phylaid=id2, classid=id3, orderid=id4, familyid=id5, genusid=id6, genusName=taxon[5])
            record.save()

        if not Species.objects.filter(speciesName=taxon[6]).exists():
            id7 = uuid4().hex
            id6 = Genus.objects.get(genusName=taxon[5])
            id5 = Family.objects.get(familyName=taxon[4])
            id4 = Order.objects.get(orderName=taxon[3])
            id3 = Class.objects.get(className=taxon[2])
            id2 = Phyla.objects.get(phylaName=taxon[1])
            id1 = Kingdom.objects.get(kingdomName=taxon[0])
            record = Species(kingdomid=id1, phylaid=id2, classid=id3, orderid=id4, familyid=id5, genusid=id6, speciesid=id7, speciesName=taxon[6])
            record.save()


def parse_profile(taxonomy, shared, path):
    f = izip(*csv.reader(shared, delimiter='\t'))
    outfile = "/".join([path, "shared.tr"])
    csv.writer(open(outfile, 'wb'), delimiter='\t').writerows(f)
    for line in fileinput.input(outfile, inplace=True):
        line = line.rstrip()
        if fileinput.lineno() == 1 or fileinput.lineno() == 3:
            continue
        print line
