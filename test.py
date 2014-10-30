
import json

import logging

import requests

import voip_db

import functions

import mail

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG,filename = u'log.log')


print "Done"


postData = {'grant_type': 'client_credentials'}
cred = {'auto_epm_voip_user', '1@qWaS34'}


logging.info( u'Send token request...' )
print 'Send token request...'
response = requests.post('https://upsa.epam.com/workload/rest/oauth/token',
                         auth=('auto_epm_voip_user', '1@qWaS34'), data=postData)
data = response.json()
token = data['value']
logging.info( u'Token recieved: ' + token )
print 'Token recieved: ' + token

headers = {'Authorization': 'Bearer ' + token}
para = {'dismissedAt': 'gt~22-oct-2014'}
#para = {'onlyActive': 'true'}
data = 'https://upsa.epam.com/workload/rest/v3/employees?dismissedAt=gt~22-oct-2014'
response = requests.get(data, headers=headers)
data = response.json()
count=0
for row in data:
    count = count + 1
    print str(row['fullName']) +':'+str(int(row['isActive']))
print count

"""L = [1,
4000610700000000366,
4000741334650022057,
4000741400000172700,
4000741400000891186,
4000741400014103185,
4060741400005350099,
4060741400006359973,
4060741400007057190,
4060741400007057217,
4060741400007057219,
4060741400007057221,
4060741400007057224,
4060741400007057226,
4060741400007066556,
4060741400007625828,
4060741400007701920,
4060741400007905985,
4060741400008050891,
4060741400008050893,
4060741400008117181,
4060741400008240077,
4060741400008475909,
4060741400008484196,
4060741400008564725,
4060741400008630093,
4060741400008638983,
4060741400008719288,
4060741400008810204]

for l in L:
	print "insert into [voip_new].[dbo].[numranges] values (%s,56500,56799)" % str(l)
	print "insert into [voip_new].[dbo].[numranges] values (%s,59400,59499)" % str(l)
	print "insert into [voip_new].[dbo].[numranges] values (%s,41000,41099)" % str(l)
	print "insert into [voip_new].[dbo].[numranges] values (%s,41800,41999)" % str(l)
	print "insert into [voip_new].[dbo].[numranges] values (%s,59200,59399)" % str(l)"""