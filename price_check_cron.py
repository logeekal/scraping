#!/usr/bin/env python


import subprocess
from pymongo import MongoClient as mongo
import amazon_item

conn = mongo('192.168.48.128',27017)
db = conn['test-database']
coll = db['test-collection']
null =None
curr = coll.find({'act_stat':'y', 'user' :{'$not' :{'$eq' : null}}})

for item in curr:
	user = item['user'].encode('utf8')
	url = item['url'].encode('utf8')
	print "Running Script for %s and  %s" % (user, url)
	try:
		amazon_item.main(user, url)
	except Exception as e:
		print "Error Occurred :::::::::::::::::::::::::::::::::::::::::::::::::::: \n"
