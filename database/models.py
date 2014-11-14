from django.db import models
from django_extensions.db.fields import UUIDField


class Project(models.Model):
    projectid = UUIDField(primary_key=True, editable=True)
    path = models.CharField(max_length=90)
    upload_date = models.CharField(max_length=45)
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
    sampleid = UUIDField(primary_key=True, editable=True)
    projectid = models.ForeignKey(Project)
    sample_name = models.CharField(max_length=45, blank=True)
    site_name = models.CharField(max_length=90, blank=True)
    plot_name = models.CharField(max_length=90, blank=True)
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
    soil_pH = models.CharField(max_length=45, blank=True)
    tot_carb = models.CharField(max_length=45, blank=True)
    tot_nitro = models.CharField(max_length=45, blank=True)
    user_1 = models.CharField(max_length=45, blank=True)
    user_2 = models.CharField(max_length=45, blank=True)
    user_3 = models.CharField(max_length=45, blank=True)
    user_4 = models.CharField(max_length=45, blank=True)
    user_5 = models.CharField(max_length=45, blank=True)
    user_6 = models.CharField(max_length=45, blank=True)


class Kingdom(models.Model):
    kingdomid = UUIDField(primary_key=True, editable=True)
    kingdomName = models.CharField(max_length=90, blank=True)


class Phyla(models.Model):
    kingdomid = models.ForeignKey(Kingdom)
    phylaid = UUIDField(primary_key=True, editable=True)
    phylaName = models.CharField(max_length=90, blank=True)


class Class(models.Model):
    kingdomid = models.ForeignKey(Kingdom)
    phylaid = models.ForeignKey(Phyla)
    classid = UUIDField(primary_key=True, editable=True)
    className = models.CharField(max_length=90, blank=True)


class Order(models.Model):
    kingdomid = models.ForeignKey(Kingdom)
    phylaid = models.ForeignKey(Phyla)
    classid = models.ForeignKey(Class)
    orderid = UUIDField(primary_key=True, editable=True)
    orderName = models.CharField(max_length=90, blank=True)


class Family(models.Model):
    kingdomid = models.ForeignKey(Kingdom)
    phylaid = models.ForeignKey(Phyla)
    classid = models.ForeignKey(Class)
    orderid = models.ForeignKey(Order)
    familyid = UUIDField(primary_key=True, editable=True)
    familyName = models.CharField(max_length=90, blank=True)


class Genus(models.Model):
    kingdomid = models.ForeignKey(Kingdom)
    phylaid = models.ForeignKey(Phyla)
    classid = models.ForeignKey(Class)
    orderid = models.ForeignKey(Order)
    familyid = models.ForeignKey(Family)
    genusid = UUIDField(primary_key=True, editable=True)
    genusName = models.CharField(max_length=90, blank=True)


class Species(models.Model):
    kingdomid = models.ForeignKey(Kingdom)
    phylaid = models.ForeignKey(Phyla)
    classid = models.ForeignKey(Class)
    orderid = models.ForeignKey(Order)
    familyid = models.ForeignKey(Family)
    genusid = models.ForeignKey(Genus)
    speciesid = UUIDField(primary_key=True, editable=True)
    speciesName = models.CharField(max_length=90, blank=True)

