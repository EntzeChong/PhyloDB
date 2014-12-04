from django.db import models
from django_extensions.db.fields import UUIDField
from django_tables2 import tables

"""ACTIVE = 'active'
INACTIVE = 'inactive'
TERMINATED = 'terminated'

ACTIVE_CHOICES = (
    (ACTIVE, "Active"),
    (INACTIVE, "Inactive"),
    (TERMINATED, "Terminated"),
)

ACTIVE_CHOICES_DISPLAY = dict(ACTIVE_CHOICES)"""

class Project(models.Model):
    projectid = UUIDField(primary_key=True, editable=True)
    path = models.CharField(max_length=90)
    upload_date = models.CharField(max_length=15, blank=True)
    project_name = models.CharField(max_length=90, blank=True)
    project_desc = models.TextField(blank=True)
    start_date = models.CharField(max_length=15, blank=True)
    end_date = models.CharField(max_length=15, blank=True)
    pi_last = models.CharField(max_length=45, blank=True)
    pi_first = models.CharField(max_length=45, blank=True)
    pi_affiliation = models.CharField(max_length=45, blank=True)
    pi_email = models.CharField(max_length=100, blank=True)
    pi_phone = models.CharField(max_length=15, blank=True)


class Sample(models.Model):

    #active = models.CharField(max_length=10, choices=ACTIVE_CHOICES)

    sampleid = UUIDField(primary_key=True, editable=True)
    projectid = models.ForeignKey(Project)
    sample_name = models.CharField(max_length=45, blank=False)
    organism = models.CharField(max_length=90, blank=True)
    title = models.TextField(blank=True)
    seq_method = models.CharField(max_length=45, blank=True)
    collection_date = models.CharField(max_length=15, blank=True)
    biome = models.CharField(max_length=45, blank=True)
    feature = models.CharField(max_length=45, blank=True)
    geo_loc = models.CharField(max_length=45, blank=True)
    lat_lon = models.CharField(max_length=45, blank=True)
    material = models.CharField(max_length=45, blank=True)
    elevation = models.CharField(max_length=45, blank=True)

    def natural_key(self):
        return self.sampleid


class Collect(models.Model):
    sampleid = models.ForeignKey(Sample)
    projectid = models.ForeignKey(Project)
    depth = models.CharField(max_length=45, blank=True)
    pool_dna_extracts = models.CharField(max_length=45, blank=True)
    samp_size = models.CharField(max_length=45, blank=True)
    samp_collection_device = models.CharField(max_length=45, blank=True)
    samp_weight_dna_ext = models.CharField(max_length=45, blank=True)
    sieving = models.CharField(max_length=45, blank=True)
    storage_cond = models.CharField(max_length=45, blank=True)

    def natural_key(self):
        return self.sampleid


class Climate(models.Model):
    sampleid = models.ForeignKey(Sample)
    projectid = models.ForeignKey(Project)
    annual_season_precpt = models.CharField(max_length=45, blank=True)
    annual_season_temp = models.CharField(max_length=45, blank=True)

    def natural_key(self):
        return self.sampleid


class Soil_class(models.Model):
    sampleid = models.ForeignKey(Sample)
    projectid = models.ForeignKey(Project)
    bulk_density = models.CharField(max_length=45, blank=True)
    drainage_class = models.CharField(max_length=45, blank=True)
    fao_class = models.CharField(max_length=45, blank=True)
    horizon = models.CharField(max_length=45, blank=True)
    local_class = models.CharField(max_length=45, blank=True)
    porosity = models.CharField(max_length=45, blank=True)
    profile_position = models.CharField(max_length=45, blank=True)
    slope_aspect = models.CharField(max_length=45, blank=True)
    slope_gradient = models.CharField(max_length=45, blank=True)
    soil_type = models.CharField(max_length=45, blank=True)
    texture_class = models.CharField(max_length=45, blank=True)
    water_content_soil = models.CharField(max_length=45, blank=True)

    def natural_key(self):
        return self.sampleid


class Soil_nutrient(models.Model):
    sampleid = models.ForeignKey(Sample)
    projectid = models.ForeignKey(Project)
    pH = models.CharField(max_length=45, blank=True)
    EC = models.CharField(max_length=45, blank=True)
    tot_C = models.CharField(max_length=45, blank=True)
    tot_OM = models.CharField(max_length=45, blank=True)
    tot_N = models.CharField(max_length=45, blank=True)
    NO3_N = models.CharField(max_length=45, blank=True)
    NH4_N = models.CharField(max_length=45, blank=True)
    P = models.CharField(max_length=45, blank=True)
    K = models.CharField(max_length=45, blank=True)
    S = models.CharField(max_length=45, blank=True)
    Zn = models.CharField(max_length=45, blank=True)
    Fe = models.CharField(max_length=45, blank=True)
    Cu = models.CharField(max_length=45, blank=True)
    Mn = models.CharField(max_length=45, blank=True)
    Ca = models.CharField(max_length=45, blank=True)
    Mg = models.CharField(max_length=45, blank=True)
    Na = models.CharField(max_length=45, blank=True)
    B = models.CharField(max_length=45, blank=True)

    def natural_key(self):
        return self.sampleid


class Management(models.Model):
    sampleid = models.ForeignKey(Sample)
    projectid = models.ForeignKey(Project)
    agrochem_addition = models.CharField(max_length=45, blank=True)
    biological_amendment = models.CharField(max_length=45, blank=True)
    cover_crop = models.CharField(max_length=45, blank=True)
    crop_rotation = models.CharField(max_length=45, blank=True)
    cur_land_use = models.CharField(max_length=45, blank=True)
    cur_vegetation = models.CharField(max_length=45, blank=True)
    cur_crop = models.CharField(max_length=45, blank=True)
    cur_cultivar = models.CharField(max_length=45, blank=True)
    organic = models.CharField(max_length=45, blank=True)
    previous_land_use = models.CharField(max_length=45, blank=True)
    soil_amendments = models.CharField(max_length=45, blank=True)
    tillage = models.CharField(max_length=45, blank=True)

    def natural_key(self):
        return self.sampleid


class Microbial(models.Model):
    sampleid = models.ForeignKey(Sample)
    projectid = models.ForeignKey(Project)
    rRNA_copies = models.CharField(max_length=45, blank=True)
    microbial_biomass_C = models.CharField(max_length=45, blank=True)
    microbial_biomass_N = models.CharField(max_length=45, blank=True)
    microbial_respiration = models.CharField(max_length=45, blank=True)

    def natural_key(self):
        return self.sampleid


class User(models.Model):
    sampleid = models.ForeignKey(Sample)
    projectid = models.ForeignKey(Project)
    usr_cat1 = models.CharField(max_length=45, blank=True)
    usr_cat2 = models.CharField(max_length=45, blank=True)
    usr_cat3 = models.CharField(max_length=45, blank=True)
    usr_cat4 = models.CharField(max_length=45, blank=True)
    usr_cat5 = models.CharField(max_length=45, blank=True)
    usr_cat6 = models.CharField(max_length=45, blank=True)
    usr_quant1 = models.CharField(max_length=45, blank=True)
    usr_quant2 = models.CharField(max_length=45, blank=True)
    usr_quant3 = models.CharField(max_length=45, blank=True)
    usr_quant4 = models.CharField(max_length=45, blank=True)
    usr_quant5 = models.CharField(max_length=45, blank=True)
    usr_quant6 = models.CharField(max_length=45, blank=True)

    def natural_key(self):
        return self.sampleid


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


class Profile(models.Model):
    projectid = models.ForeignKey(Project)
    sampleid = models.ForeignKey(Sample)
    kingdomid = models.ForeignKey(Kingdom)
    phylaid = models.ForeignKey(Phyla)
    classid = models.ForeignKey(Class)
    orderid = models.ForeignKey(Order)
    familyid = models.ForeignKey(Family)
    genusid = models.ForeignKey(Genus)
    speciesid = models.ForeignKey(Species)
    count = models.IntegerField()
    binary = models.IntegerField()


class ProfileKingdom(models.Model):
    projectid = models.ForeignKey(Project)
    sampleid = models.ForeignKey(Sample)
    kingdomid = models.ForeignKey(Kingdom)
    count = models.IntegerField()
    rel_abund = models.DecimalField(max_digits=7, decimal_places=6)
    rich = models.IntegerField()


class ProfilePhyla(models.Model):
    projectid = models.ForeignKey(Project)
    sampleid = models.ForeignKey(Sample)
    phylaid = models.ForeignKey(Phyla)
    count = models.IntegerField()
    rel_abund = models.DecimalField(max_digits=7, decimal_places=6)
    rich = models.IntegerField()


class ProfileClass(models.Model):
    projectid = models.ForeignKey(Project)
    sampleid = models.ForeignKey(Sample)
    classid = models.ForeignKey(Class)
    count = models.IntegerField()
    rel_abund = models.DecimalField(max_digits=7, decimal_places=6)
    rich = models.IntegerField()


class ProfileOrder(models.Model):
    projectid = models.ForeignKey(Project)
    sampleid = models.ForeignKey(Sample)
    orderid = models.ForeignKey(Order)
    count = models.IntegerField()
    rel_abund = models.DecimalField(max_digits=7, decimal_places=6)
    rich = models.IntegerField()


class ProfileFamily(models.Model):
    projectid = models.ForeignKey(Project)
    sampleid = models.ForeignKey(Sample)
    familyid = models.ForeignKey(Family)
    count = models.IntegerField()
    rel_abund = models.DecimalField(max_digits=7, decimal_places=6)
    rich = models.IntegerField()


class ProfileGenus(models.Model):
    projectid = models.ForeignKey(Project)
    sampleid = models.ForeignKey(Sample)
    genusid = models.ForeignKey(Genus)
    count = models.IntegerField()
    rel_abund = models.DecimalField(max_digits=7, decimal_places=6)
    rich = models.IntegerField()


class ProfileSpecies(models.Model):
    projectid = models.ForeignKey(Project)
    sampleid = models.ForeignKey(Sample)
    speciesid = models.ForeignKey(Species)
    count = models.IntegerField()
    rel_abund = models.DecimalField(max_digits=7, decimal_places=6)
    rich = models.IntegerField()

class SampleTable(tables.Table):
    class Meta:
        model = Sample

class CollectTable(tables.Table):
    class Meta:
        model = Collect

class ClimateTable(tables.Table):
    class Meta:
        model = Climate

class Soil_classTable(tables.Table):
    class Meta:
        model = Soil_class

class Soil_nutrientTable(tables.Table):
    class Meta:
        model = Soil_nutrient

class ManagementTable(tables.Table):
    class Meta:
        model = Management

class MicrobialTable(tables.Table):
    class Meta:
        model = Microbial

class UserTable(tables.Table):
    class Meta:
        model = User
