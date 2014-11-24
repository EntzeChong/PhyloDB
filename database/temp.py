'''
myDict = {}
var = [u'sample_name:RENG8|sample_name:CBG6|sample_name:ESRBG24|sample_name:CBG4|sample_name:RENG12|sample_name:CBG26|sample_name:RENG25|sample_name:ESRBG27|sample_name:RENG26|sample_name:CBG13|sample_name:CBG1|sample_name:RENG29|sample_name:CBG30|sample_name:CBG10|sample_name:RENG21|sample_name:RENG13|sample_name:CBG27|sample_name:CBG19|sample_name:RENG32|sample_name:ESRBG3|sample_name:RENG2|sample_name:ESRBG11|sample_name:ESRBG18|sample_name:ESRBG31|sample_name:CBG16|sample_name:ESRBG20|sample_name:ESRBG5|sample_name:ESRBG9|sample_name:ESRBG14|sample_name:RENG7|MIMARKs:sample_name']
var2 = str(var)
var2 = var2.replace("[u'", "")
var2 = var2.replace("']", "")
print var
print var2
new = var2.split("|")
print new
c=0[{'sum': 52, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'0480e315554f44c3b9d80236f1f33954'}, {'sum': 129, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'189bd1ef445540afab75ba3805eef3fe'}, {'sum': 535, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'1ee82478fbf64111aa45667442710926'}, {'sum': 4, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'3869dc76d1694c62aa1a30b7389a5211'}, {'sum': 120, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'47c1ac16c17b421dadaa04f4170605f2'}, {'sum': 4, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'56d5c5f55c414d4c8151f7137b9a8a6e'}, {'sum': 4, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'5db43a0a844545dfabd5185a3fff3873'}, {'sum': 8, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'5f2dc6de454a49bc86b510e74f685f7e'}, {'sum': 14, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'60d3c3d061ed4312bde1b8d0aa0e84de'}, {'sum': 47, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'640fbfa17f13434fa6b118f8c336f614'}, {'sum': 499, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'657bd30f342a4b3b97562baf56cb2b6f'}, {'sum': 34, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'69452af544de41d8bd4ffeacca06f5b8'}, {'sum': 3, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'6d1ea9e2eede4f4ba195e21e05b29262'}, {'sum': 476, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'89e7993e9fd4478d83cc4f82da8f8bdc'}, {'sum': 2, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'8fa14f0e529e4e13b4b4a806bc5c9c83'}, {'sum': 6, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'9ac990ed309f4fb6b399c6480e8fce12'}, {'sum': 65, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'b6d3ef4b21bd405e946d34ffb7bd90ed'}, {'sum': 3, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'b7249a2c0f2d473e8e71d062a6858a15'}, {'sum': 1439, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'b860a20cd23843a0a81e2a9aff139c0c'}, {'sum': 14, 'phylaid': u'3d2a33491d6d43b0b692533baa490813', 'sampleid': u'b876a4c00ee64ca1945f6df31977be17'}
while c<new.__len__():
    data = new[c].split(":")
    key = str(data[0])
    value = str(data[1])
    myDict.setdefault(key, [])
    myDict[key].append(value)
    c+=1
print("THIS IS THE DICTIONARY:")
print myDict
#myNode5['sample_name'].append(myNode6)
'''

finalDict = {
    "rel_abund": [
        {
            "x_values": ["CBG", "ESR", "REN"],
            "name": "Proteobacteria",
            "y_values": [0.3958213, 0.3859393, 0.36084]
        },
        {
            "x_values": ["CBG", "ESR", "REN"],
            "name": "Rhizobiales",
            "y_values": [0.0667671, 0.04395400000000001, 0.034673899999999994]
        },
        {
            "x_values": ["CBG", "ESR", "REN"],
            "name": "Alphaproteobacteria",
            "y_values": [0.08572700000000001, 0.14687860000000003, 0.1118252]
        }],
    "richness": [
        {
            "x_values": ["CBG", "ESR", "REN"],
            "name": "Proteobacteria",
            "y_values": [21.5, 43.1, 39.0]
        },
        {
            "x_values": ["CBG", "ESR", "REN"],
            "name": "Rhizobiales",
            "y_values": [3.1, 6.1, 5.4]
        },
        {
            "x_values": ["CBG", "ESR", "REN"],
            "name": "Alphaproteobacteria",
            "y_values": [5.6, 17.1, 15.1]
        }
    ]}

#parse final dict
rel_abund = finalDict['rel_abund']
print 'rel_abund:'
for i in rel_abund:
    print 'series -> ' + str(i['name'])
    print 'x-values -> ' + str(i['x_values'])
    print 'y-values -> ' + str(i['y_values'])

print
richness = finalDict['richness']
print 'richness:'
for i in richness:
    print 'series -> ' + str(i['name'])
    print 'x-values -> ' + str(i['x_values'])
    print 'y-values -> ' + str(i['y_values'])