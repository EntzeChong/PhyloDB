from django.db import models


class Project(models.Model):
    projectid = models.CharField(max_length=45, primary_key=True)
    project_name = models.CharField(max_length=45, blank=True)
    project_desc = models.TextField(max_length=255, blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    pi_last = models.CharField(max_length=45, blank=True)
    pi_first = models.CharField(max_length=45, blank=True)
    pi_affiliation = models.CharField(max_length=45, blank=True)
    pi_email = models.CharField(max_length=100, blank=True)
    pi_phone = models.CharField(max_length=15, blank=True)


class Sample(models.Model):
    sampleid = models.CharField(max_length=45, primary_key=True)
    projectid = models.ForeignKey(Project)
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
    cur_land = models.CharField(max_length=45, blank=True)
    cur_crop = models.CharField(max_length=45, blank=True)
    cur_cultivar = models.CharField(max_length=45, blank=True)
    microbial_biomass = models.CharField(max_length=45, blank=True)
    biomass_gene = models.CharField(max_length=45, blank=True)
    profile_position = models.CharField(max_length=45, blank=True)
    soil_type = models.CharField(max_length=45, blank=True)
    tillage = models.CharField(max_length=45, blank=True)
    water_content = models.CharField(max_length=45, blank=True)
    ph = models.CharField(max_length=45, blank=True)
    tot_carb = models.CharField(max_length=45, blank=True)
    tot_nitro = models.CharField(max_length=45, blank=True)
    user1 = models.CharField(max_length=45, blank=True)
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
    sampleid = models.ForeignKey(Sample)
    t_kingdom = models.CharField(max_length=45, blank=True)
    t_phylum = models.CharField(max_length=45, blank=True)
    t_class = models.CharField(max_length=45, blank=True)
    t_order = models.CharField(max_length=45, blank=True)
    t_family = models.CharField(max_length=45, blank=True)
    t_genus = models.CharField(max_length=45, blank=True)
    t_species = models.CharField(max_length=45, blank=True)
    seqreads = models.IntegerField(blank=True)


class Document1(models.Model):
    docfile1 = models.FileField(upload_to='temp')


class Document2(models.Model):
    docfile2 = models.FileField(upload_to='temp')


class Document3(models.Model):
    docfile3 = models.FileField(upload_to='temp')


class Document4(models.Model):
    docfile4 = models.FileField(upload_to='temp')

