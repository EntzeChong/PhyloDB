from django.db import models


class Project(models.Model):
    ProjectID = models.CharField(max_length=45, primary_key=True)
    project_name = models.CharField(max_length=45, blank=True)
    project_desc = models.TextField(blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    PI_last = models.CharField(max_length=50, blank=True)
    PI_first = models.CharField(max_length=50, blank=True)
    PI_affiliation = models.CharField(max_length=50, blank=True)
    PI_email = models.TextField(blank=True)
    PI_phone = models.CharField(max_length=15, blank=True)


class Sample(models.Model):
    SampleID = models.CharField(max_length=45, primary_key=True)
    ProjectID = models.ForeignKey('Project', to_field='ProjectID', related_name='ProjectID_12')
    sample_name = models.CharField(max_length=45, blank=True)
    organism = models.CharField(max_length=45, blank=True)
    title = models.CharField(max_length=250, blank=True)
    seq_method = models.CharField(max_length=45, blank=True)
    collection_date = models.DateField(blank=True)
    biome = models.CharField(max_length=45, blank=True)
    feature = models.CharField(max_length=45, blank=True)
    geo_loc = models.CharField(max_length=45, blank=True)
    lat_lon = models.CharField(max_length=45, blank=True)
    material = models.CharField(max_length=45, blank=True)
    depth = models.CharField(max_length=45, blank=True)
    elevation = models.CharField(max_length=45, blank=True)
    crop_rotation = models.CharField(max_length=45, blank=True)
    cur_land_use = models.CharField(max_length=45, blank=True)
    cur_crop = models.CharField(max_length=45, blank=True)
    cur_cultivar = models.CharField(max_length=45, blank=True)
    microbial_biomass = models.CharField(max_length=45, blank=True)
    biomass_gene_copy_num = models.CharField(max_length=45, blank=True)
    profile_position = models.CharField(max_length=45, blank=True)
    soil_type = models.CharField(max_length=45, blank=True)
    tillage = models.CharField(max_length=45, blank=True)
    water_content_soil = models.CharField(max_length=45, blank=True)
    pH = models.CharField(max_length=45, blank=True)
    tot_org_carb = models.CharField(max_length=45, blank=True)
    tot_nitro = models.CharField(max_length=45, blank=True)
    user1 = models.CharField(max_length=45, blank=True) # what are these for? should be another table relating user to sampleID
    user2 = models.CharField(max_length=45, blank=True)
    user3 = models.CharField(max_length=45, blank=True)
    user4 = models.CharField(max_length=45, blank=True)
    user5 = models.CharField(max_length=45, blank=True)
    user6 = models.CharField(max_length=45, blank=True)
    user7 = models.CharField(max_length=45, blank=True)
    user8 = models.CharField(max_length=45, blank=True)
    user9 = models.CharField(max_length=45, blank=True)
    user10 = models.CharField(max_length=45, blank=True)
    user11 = models.CharField(max_length=45, blank=True)
    user12 = models.CharField(max_length=45, blank=True)


class Taxonomy(models.Model):
    SampleID = models.ForeignKey('Sample', to_field='SampleID', related_name='SampleID_50')
    Kingdom = models.CharField(max_length=45)
    Phylum = models.CharField(max_length=45)
    Class = models.CharField(max_length=45)
    Order = models.CharField(max_length=45)
    Family = models.CharField(max_length=45)
    Genus = models.CharField(max_length=45)
    Species = models.CharField(max_length=45)
    SeqReads = models.IntegerField(blank=True)


class Document1(models.Model):
    docfile1 = models.FileField(upload_to='%Y.%m.%d')


class Document2(models.Model):
    docfile2 = models.FileField(upload_to='%Y.%m.%d')


class Document3(models.Model):
    docfile3 = models.FileField(upload_to='%Y.%m.%d')


class Document4(models.Model):
    docfile4 = models.FileField(upload_to='%Y.%m.%d')

