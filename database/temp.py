import re
import csv
import fileinput
from uuid import uuid4
from itertools import izip

from models import Project, Sample, Taxa, Kingdom, Phyla, Class, Order, Family, Genus, Species


def parse_taxonomy(filepath, filename, p_uuid):
    inFile = "/".join([str(filepath), str(filename)])
    for line in fileinput.input(inFile, inplace=True):
        line = line.rstrip()
        print(re.sub(r'\(.*?\)', '', line))
    f = csv.DictReader(open(inFile, 'r'), delimiter='\t')
    for row in f:
        otu = row["OTU"]
        taxa = row["Taxonomy"]
        project = Project.objects.get(projectid=p_uuid)
        k = Taxa(projectid=project, taxa=taxa, otuid=otu)
        k.save()

        taxon = taxa.split(';')
        if not Kingdom.objects.filter(t_kingdom=taxon[0]).exists():
            id = uuid4().hex
            dict = {'t_kingdom': taxon[0]}
            record = Kingdom(kingdomid=id, **dict)
            record.save()
        if not Phyla.objects.filter(t_phyla=taxon[1]).exists():
            id = uuid4().hex
            dict = {'t_phyla': taxon[1]}
            id2 = Kingdom.objects.get(t_kingdom=taxon[0])
            record = Phyla(kingdomid=id2, phylaid=id, **dict)
            record.save()
        if not Class.objects.filter(t_class=taxon[2]).exists():
            id = uuid4().hex
            dict = {'t_class': taxon[2]}
            id2 = Phyla.objects.get(t_phyla=taxon[1])
            record = Class(phylaid=id2, classid=id, **dict)
            record.save()
        if not Order.objects.filter(t_order=taxon[3]).exists():
            id = uuid4().hex
            dict = {'t_order': taxon[3]}
            id2 = Class.objects.get(t_class=taxon[2])
            record = Order(classid=id2, orderid=id, **dict)
            record.save()
        if not Family.objects.filter(t_family=taxon[4]).exists():
            id = uuid4().hex
            dict = {'t_family': taxon[4]}
            id2 = Order.objects.get(t_order=taxon[3])
            record = Family(orderid=id2, familyid=id, **dict)
            record.save()
        if not Genus.objects.filter(t_genus=taxon[5]).exists():
            id = uuid4().hex
            dict = {'t_genus': taxon[5]}
            id2 = Family.objects.get(t_family=taxon[4])
            record = Genus(familyid=id2, genusid=id, **dict)
            record.save()
        if not Species.objects.filter(t_species=taxon[6]).exists():
            id = uuid4().hex
            dict = {'t_species': taxon[6]}
            id2 = Genus.objects.get(t_genus=taxon[5])
            record = Species(genusid=id2, speciesid=id, **dict)
            record.save()




def parse_profile(filepath, taxonomy, shared, p_uuid):
    inFile1 = "/".join([str(filepath), str(taxonomy)])
    taxa_list = []
    for line in fileinput.input(inFile1):
        if not fileinput.isfirstline():
            line = line.rstrip()
            fields = line.split('\t')
            taxa_list.append(fields[2])
    inFile2 = "/".join([str(filepath), str(shared)])
    lis = izip(*csv.reader(open(inFile2, 'rb'), delimiter='\t'))
    outfile = "/".join([str(filepath), str(shared+".tr")])
    csv.writer(open(outfile, 'wb'), delimiter='\t').writerows(lis)
    for line in fileinput.input(outfile, inplace=True):
        line = line.rstrip()
        if fileinput.lineno() == 1 or fileinput.lineno() == 3:
            continue
        print(line)
    samples_list = {}
    for line in fileinput.input(outfile):
        if fileinput.lineno() == 1:
            line = line.rstrip()
            samples_list = line.split('\t')
    samples_list.pop(0)
    g = csv.reader(open(outfile, 'r'), delimiter='\t')
    g.next()
    j = 0
    for line in g:
        for i in range(len(samples_list)):
            count = line[i+1]
            if count > 0:
                taxon = taxa_list[j].split(';')
                name = samples_list[i]
                project = Project.objects.get(projectid=p_uuid)
                sample = Sample.objects.filter(projectid=p_uuid).get(sample_name=name)
                t_kingdom = Kingdom.objects.get(t_kingdom=taxon[0])
                t_phyla = Phyla.objects.get(t_phyla=taxon[1])
                t_class = Class.objects.get(t_class=taxon[2])
                t_order = Order.objects.get(t_order=taxon[3])
                t_family = Family.objects.get(t_family=taxon[4])
                t_genus = Genus.objects.get(t_genus=taxon[5])
                t_species = Species.objects.get(t_species=taxon[6])
                record = Profile(projectid=project, sampleid=sample, kingdomid=t_kingdom, phylaid=t_phyla, classid=t_class, orderid=t_order, familyid=t_family, genusid=t_genus, speciesid=t_species, count=count)
                record.save()
        j += 1



def parse_profiledoc(Document, p_uuid):
    taxa_list = []
    for line in Document:
        line = line.rstrip()
        fields = line.split('\t')
        print(taxa_list)
        c =0
        while c<fields[2]:
            taxa_list.append(fields[c+2])
            c+=1
    print(taxa_list)