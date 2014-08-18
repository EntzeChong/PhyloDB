import csv
from database.models import Project, Sample, Taxonomy
import uuid


def Update(request):
    doc1 = open('uploads/%Y/%m/%d/meta_Project.csv', 'r')
    data1 = csv.reader(doc1, delimiter=',')
    # generate unique project ID, only one project at a time can be processed
    p_uuid = str(uuid.uuid1().int)
    next(data1, None)
    for row in data1:
        print(
            Project(ProjectID=p_uuid,
                    project_name=row[0],
                    project_desc=row[1],
                    start_date=row[2],
                    end_date=row[3],
                    PI_last=row[4],
                    PI_firstrow=row[5],
                    PI_affiliation=row[6],
                    PI_email=row[7],
                    PI_phone=row[8]
            )
        )
    doc2 = open('uploads/%Y/%m/%d/meta_Sample.csv', 'r')
    data2 = csv.reader(doc2, delimiter=',')

    for row in data2:
        s_uuid = str(uuid.uuid1().int)
        projectid, _ = Project.objects.get_or_create(name=row[0])
        next(data2, None)
        print(
            Project(SampleID=s_uuid,
                    ProjectID=p_uuid,
                    sample_name=row[0],
                    organism=row[1],
                    title=row[2],
                    seq_method=row[3],
                    collection_date=row[4],
                    biome=row[5],
                    feature=row[6],
                    geo_loc_name=row[7],
                    lat_long=row[9],
                    material=row[10],
                    depth=row[11],
                    elevation=row[12],
                    crop_rotation=row[13],
                    cur_land_use=row[14],
                    cur_crop=row[15],
                    cur_cultivar=row[16],
                    microbial_biomass=row[17],
                    biomass_gene_copy_num=row[18],
                    profile_position=row[19],
                    soil_type=row[20],
                    tillage=row[21],
                    water_content_soil=row[22],
                    pH=row[23],
                    tot_org_carb=row[24],
                    tot_nitro=row[25],
                    user1=row[26],
                    user2=row[27],
                    user3=row[28],
                    user4=row[29],
                    user5=row[30],
                    user6=row[31],
                    user7=row[32],
                    user8=row[33],
                    user9=row[34],
                    user10=row[35],
                     user11=row[36],
                    user12=row[37]
            )
        )