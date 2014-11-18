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
c=0
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

