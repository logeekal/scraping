import re
import requests
import json
import ast
from bs4 import BeautifulSoup
from bs4.element import Tag
import sys

url = sys.argv[1]
#print url

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
item_details['rating'] = rating
item_details['title'] =  title
item_details['avail'] = avail
item_details['price'] = price_details

print json.dumps(item_details, indent=2)


def send_alert(item_det):
	import smtplib  #sending Function
	from email.mime.text import MIMEText  	#import email libraries
	mail_text  = json.dumps(item_det,indent=2)
	print item_det['title']
	
	msg = MIMEText(mail_text)
	msg['subject'] = 'Amazon Price alert'
	me = 'jtn.kathuria@gmail.com'
	msg['from'] = me
	msg['to'] = me
	
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
	doc = {}
	doc['Name'] = item_details['title']
	all = string.maketrans('','')
	doc['Availability'] = item_details['avail'].encode('utf8').translate(all, all.translate(all, string.letters + ' '))
	doc['Price'] = []
	doc['Price'].append(item_details['price'])
	doc['rating'] = item_details['rating']
	coll.insert(doc)	
insert_db(item_details)

'''
try:
	send_alert(item_details)
	print 'mail sent'
except Exception as e:
	print e
'''	
