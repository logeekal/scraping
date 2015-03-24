import re
import requests
import json
import ast
from bs4 import BeautifulSoup
from bs4.element import Tag
import sys
import string


#print url
if len(sys.argv) > 1:
	url = sys.argv[1]
	email = 'jtn.kathuria@gmail.com'
	print url, email

def send_alert(original, item_det):
	import smtplib  #sending Function
	from email.mime.text import MIMEText  	#import email libraries
	print type(item_det)
	text = """
	<html>
	<head>
	</head>
	<body>
	This is the Price Alert for the product you are tracking.
	<h1>You can visit the product <a href = %s> here </h1>
	<h2>	<pre>	%s </pRe></h2>
	</body>
	</html>
	"""
	text_additional = ''
	if original is None:
		text_additional = 'First Time Alert %s' % json.dumps(item_det,indent=2)
	else:
		text_additional = 'Original is:  \n %s and New prices are : \n %s' % (json.dumps(original, indent=2), json.dumps(item_det, indent=2)) 
	mail_text  = text % (item_det['url'].encode('utf8'),text_additional)
	print item_det['Name']
	
	msg = MIMEText(mail_text, 'html')
	if original is None:
		title_option = ' Registeration Confirmed for %s' % item_det['Name']
	else:
		title_option = ' - %s' % item_det['Name']
	msg['subject'] = 'Amazon Price alert' + title_option
	me = 'jtn.kathuria@gmail.com'
	msg['from'] = me
	msg['to'] = item_det['user']	
	send = smtplib.SMTP('smtp.gmail.com',587)
	send.ehlo()
	send.starttls()
	send.ehlo()
	send.login('jtn.kathuria@gmail.com','intel986821121')
	send.sendmail(me, me, msg.as_string())
	send.quit()


def insert_db(item_details):
	import pymongo
	from pymongo import MongoClient as mongo
	
	client = mongo('192.168.48.128',27017)
	db = client['test-database']
	coll = db['test-collection']
	print item_details['title']	
	original = coll.find_one({'Name' : item_details['title']})

	doc = {}
	doc['Name'] = item_details['title']
	all = string.maketrans('','')
	onlyalpha = all.translate(all, string.letters +' ')
	doc['Availability'] = ' '.join(item_details['avail'].encode('utf8').translate(all, onlyalpha).split(' '))
	#doc['Price'] = []
	doc['url'] = item_details['url']
	doc['user'] =  item_details['user']
	doc['Price'] = item_details['price']
	doc['rating'] = item_details['rating']
	doc['act_stat'] =  item_details['act_stat']
	if original is not None:
		original['_id'] = ''
		if original['Price'] == doc['Price']:
			print "Price is same"
			return None, None
		else:
			print  '===================',original['Price']
			print '====================', doc['Price']	
			import copy
			doc2 = copy.copy(doc)
			coll.update({'Name':item_details['title']},{'$set' : {'Price' : item_details['price']}})	
			return original, doc2
	else:
		import copy
                doc2 = copy.copy(doc)
                #print doc2
                coll.insert(doc)
                return None, doc2	

def main(email, url):
	response = requests.get(url)

	soup =BeautifulSoup(response.text)
	try:
		rating =  soup.find_all('span', attrs = {'id' : 'acrPopover'})[0]['title']
	except IndexError:
		rating = 'Not yet Rated'
	print rating
	print '-------------------------------'

	title = soup.find_all('span', attrs = {'id' : 'productTitle'})[0].get_text()
	print title

	avail =  soup.find_all('div', attrs= {'id':'availability'})[0].get_text()
	print avail.strip()


	price_details = {}
	for child in soup.find_all('div', attrs = {"id" : "price"}):
		soup_child = child
	#	print type(soup_child)
	#	print type(soup_child.find_all('table')[0])
	#	print soup_child.find_all('table')[0].prettify()
		for rows  in soup_child.find_all('table')[0].children:
			if isinstance(rows, Tag):
				columns = rows.contents
				label = columns[1].get_text()
				value = columns[3].get_text()
			#	print label, value
				if label != '':
					#price_details[label] = [i for i in re.findall(r'[\d\,\.\d]+',value) if i.rfind('.') != -1][0]
					label =  label.replace('.','')	
					#Extra characters removing logic
					import string
					all = string.maketrans('','')
					nodigs = all.translate(all, string.digits + '.')
					value = value.encode('utf8').translate(all, nodigs)
					#removing extra decimals
					value_parts = value.split('.')
					length = len(value_parts)
					for index in range(length):
						if value_parts[index] != '.':
							value = value_parts[index] + '.' + value_parts[index + 1]					
							break	
					price_details[label] = float(value)
	#		print '\n'
	item_details = {}
	item_details['user'] = email
	item_details['rating'] = rating
	item_details['title'] =  title
	item_details['avail'] = avail
	item_details['price'] = price_details
	item_details['url'] = url
	item_details['act_stat'] = 'y'
	original,mail = insert_db(item_details)
	 
	print mail

	try:
		if mail:
			send_alert(original, mail)
			print 'mail sent'
		else:
			pass
	except Exception as e:
		print 'Error Encountered : ' + str(e)

	print json.dumps(item_details, indent=2)
import time

#main(email,url)

