from wsgiref.simple_server import make_server as server
from cgi import parse_qs, escape
import urlparse,urllib
import cgi
import amazon_item
from beaker.middleware import SessionMiddleware as SM
from pymongo import MongoClient as mongo
logout_html =  """
<a href='/logout'> Log Out </a> 
"""


main_html = logout_html +  """
<html>
<head><title>Register the Amazon URL</title></head>
<body>
	<table border=1>
	<tr>
	<td>
		<form method="post" action="/list">
			<pre>
			<h1> Register a price alert </h1>
		
			Email : <input type=text name="email">
		
			URL   : <input type=text name="url">

				<input type=Submit name="Submit">	
			</pre>
		</form>
	</td>
	<td>
		<form method="post" action="/list">
		
			<pre>
				<h1> See the list of Registered Products </h1>
				
				Email  : <input type=text name=lemail>
				
					<input type=submit name="Submit">
			</pre>
			
		</form>
	</td>
	</tr>
	<table>
%s	
	
</body>
</html>
"""

list_html = logout_html  + """
<html> 
<head><title> Registered Products  </title> </head>
<body>
	<form action="/list" method="post">
		
		URL   : <input type=text name="url"> 
		
			<input type=submit name="Submit">
	</form>
<table border=1>	
%s
</table>
</body>	
</html>
"""

def env_list(environ, start_response):
	response_body = ''
	for keys in environ.keys():
		response_body = response_body +  "%s : %s \n" % (keys, str(environ[keys]))
	start_response('200 OK',[('Content-type','text/plain'),('Content-Length', str(len(response_body)))])
	return [response_body]	


def act_toggle(environ, start_response):
	conn = mongo('192.168.48.128',27017)
	db = conn['test-database']
	coll = db['test-collection']
	
	qs = urlparse.parse_qs(environ['QUERY_STRING'])
	url = ''
	status = ''
	#print qs
	if 'name' in qs:
		name = qs['name'][0]
	if 'status' in qs:
		status = qs['status'][0]
		#print 'Status ======== %s ' % status
	if status == 'y':
		new_status = 'n'
	else:
		new_status = 'y'

	session = environ['beaker.session']
	if 'user' in session:
		user = session['user']
		#print new_status, name, user
		query = {'user': user, 'Name' : name}
		stmt = {'$set' : {'act_stat': new_status}}
		#print query, stmt
		curr = coll.update(query ,stmt)
		#print curr	
		start_response('302 Found',[('Location','/list')])	
		return ['1']
	
	else:
		start_response('302 Found',[('Location','/?e=session_invalid')])	
		return ['1']
	
def list(environ, start_response):
	user = ''
	url =''	
	session = environ['beaker.session']
#	#print session['user']
	if 'user' in session:
		
		user = session['user']

	response_body = list_html
	#print type(environ)
	#Check the Request method
	if environ['REQUEST_METHOD'] == 'POST':
		env_copy = environ.copy()
		env_copy['QUERY_STRING'] = '' 
		#above statment due to bug in field storage as 
			
		data = cgi.FieldStorage(fp = environ['wsgi.input'],
					environ = env_copy,
					keep_blank_values = 1)
		if user == '':
			user = data.getvalue('email') #if no user is set in session then new user will be read
		url = data.getvalue('url')
		
	elif environ['REQUEST_METHOD'] == 'GET':
		qs =  urlparse.parse_qs(environ['QUERY_STRING'])
		#print environ['QUERY_STRING']
		if 'email' in qs:
			user = qs['email'][0]
		if 'url' in qs:
			url = qs['url'][0]
		if 'act_toggle' in qs:
			act_toggle =  qs['act_toggle'][0]
	#print user, url		

	
	if user == '':
		#check session
		#post request for invalid session
		
		start_response('302 Found',[('Location','/?e=session_invalid')])
		#urllib.pathname2url('/e=session_invalid')),('Content-type','application/x-www-form-urlencoded')])
		return ['1']
	elif user != '' and url != '':
		if 'user' not in session:
			session['user'] = user
			session.save()
			#print "Session Set! as " + session['user']
		#print 'Setting up the alert'
		amazon_item.main(user,url)
	elif user != '' and url == '':
		if 'user' not in session:
			session['user'] = user
			session.save()
			#print "Session Set! as " + session['user']

	from pymongo import MongoClient as mongo	
	conn = mongo('192.168.48.128',27017)
	db = conn['test-database']
	coll = db['test-collection']
	res_cur = coll.find({'user' : user})		
	list_text = ""
	if res_cur is None:
		list_text = "No registered Products"
	else:
#		list_text = list_text + 'Heroooooooooo'
		p_name, p_url, p_stat = ' ', ' ', ' '
		for item in res_cur:
			
			if 'Name' in item:
				p_name =  item['Name'].encode('utf8')
			if 'url' in item:
				p_url = item['url'].encode('utf8')
			if 'act_stat' in item:
				p_stat =  item['act_stat'].encode('utf8')
			query = urllib.urlencode({'name': p_name, 'status': p_stat})
			#print query
			list_text = list_text + """<tr><td>""" + p_name + """</td><td>Visit the product <a href = """ + p_url + """> here </a> </td><td><a href=/act_toggle?""" + query +  """>"""+ p_stat + """ </td></tr>"""

	response_body =  list_html % list_text
	#print response_body	
	response_headers = [
				('Content-Type','text/html'),
				('Content-Length', str(len(response_body)))
				]
	start_response('200 OK', response_headers)
	
	return [response_body]	

def main(environ, start_response):
	
	session = environ['beaker.session']
	if 'user' in session:
		start_response('302 Found', [('Location','/list')])
		return ['1']	


	mess = ''	
	if environ['REQUEST_METHOD'] == 'GET':
		qs = urlparse.parse_qs(environ['QUERY_STRING'])
		if 'e' in qs:
			mess = qs['e'][0]
	
	if mess == 'session_invalid':
		mess = 'Please Login'
	response_body = main_html % mess
	
	status = '200 OK'
	
	response_headers = [
				('Content-Type','text/html'),
				('Content-Length', str(len(response_body)))
				]
	start_response(status, response_headers)
	
	return [response_body]

def logout(environ, start_response):
	session = environ['beaker.session']
	if 'user' in session:
		del session['user']
		session.save()
	start_response('302 Found', [('Location','/')])
	return ['1']

def app(environ, start_response):
	if environ['PATH_INFO'] == '/':
		return main(environ, start_response)
	elif environ['PATH_INFO'] == '/list':
		return list(environ, start_response)
	elif environ['PATH_INFO'] == '/env':
		return env_list(environ,start_response)
	elif environ['PATH_INFO'] == '/logout':
		return logout(environ, start_response)
	elif environ['PATH_INFO'] == '/act_toggle':
		return act_toggle(environ,start_response)

app =  SM(app, key='mysession', secret='mysecret')
httpd = server('192.168.48.128', 8051, app)
print "Servicing on port 8051 "
httpd.serve_forever()

