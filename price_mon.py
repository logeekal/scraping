from cgi import parse_qs, escape
import urllib2
import requests
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
from datetime import datetime, timedelta
import os 
import urllib
import ast

curr_path = os.getcwd()
#main_path =  os.path.join(curr_path, 'main.html')
CLIENT_SECRETS = '/home/jatin/Github/scraping/client_secrets.json'
MAIN_PATH = '/home/jatin/Github/scraping/'
layout_html = """<html><a href='/logout'> Logout <br/><br/></a> </html>"""

index_html = """
<html>
<body>
	<form method="get" action="/login">
		<p>
			Email : <input type=text name="name">
		</p>
		
		<p>
			<input type=Submit value="Submit" >
		</p>
	</form>
</body>
</html>
"""


test_html = """
<html>
<head><title> Callback </title> </head>
<body>
Thank you for the code : %s
</body>
</html>
"""

def display_env(environ,start_response):
	env_list = ['%s : %s' % (key, value) for key, value in sorted(environ.items())]
	
	response_body =  '\n'.join(env_list) 
	
	status = '200 OK'
	
	response_headers = [
						('Content-Type','text/plain'),
						('Content-Length', str(len(response_body)))
						]
						
	start_response(status, response_headers)
	
	return [response_body]

def login(environ, start_response):
	status = '200 OK'
	
	#read Client App details	
	file = open('/home/jatin/Github/scraping/client_secrets.json','r')
	SECRETS = ast.literal_eval(file.read())      #Convert to dictionary
	resp_url_params = urllib.urlencode(SECRETS['web']) #Store the parameters to pass in url
	

	scope_url = urllib.urlencode({"scope" : "https://www.googleapis.com/auth/drive"})		
	url= 'https://accounts.google.com/o/oauth2/auth?response_type=code&' + resp_url_params + '&' +  scope_url
	print url 	#Url prepared for getting the authorization code for google Oauth.
	
	start_response('304 Not Modified', [('Location',url)])   # Need to redirect the user to Google url
	
	'''response = urllib2.urlopen(url)
#	print response.read()
	
	response_headers = [
						('Content-Type','text/html'),
						('Content-Length', str(len(response.read())))
						]
	start_response(status, response_headers)
	#print response.text		
	
	response = response.read().encode('UTF-8')
	print type(response)
	return [response]'''
	return ["""<html></html>"""]
def index(environ, start_response):
	HOST = environ['REMOTE_ADDR']
	name = ''
		
	response_body = index_html
	
	status = '200 OK'
	
	response_headers = [
						('Content-Type','text/html'),
						('Content-Length', str(len(response_body)))
	                   ]
	
						
	start_response(status, response_headers)
	return [response_body]

def oauth2callback(environ, start_response):
	#Read the Authorization code sent by Google
	qs = parse_qs(environ['QUERY_STRING'])
	code = qs.get('code')[0]
	access_params = {}
	access_params['code'] = code
	'''
	#############################################################################################################
	################                            For Second CallBack 			#######################
	###############  Now request the access token with that authorization code recived   	#######################
	#############################################################################################################
	'''
	file = open(CLIENT_SECRETS,'r')
	cs = ast.literal_eval(file.read())
	cs = cs['web']	
	'''
	#######################################################################333
	POST Request with paramters with following format
	code=4/P7q7W91a-oMsCeLvIaQm6bTrgtp7&
	client_id=8819981768.apps.googleusercontent.com&
	client_secret={client_secret}&
	redirect_uri=https://oauth2-login-demo.appspot.com/code&
	grant_type=authorization_code
	########################################################################
	'''
	access_params['client_id'] = cs['client_id']
	access_params['client_secret'] = '7mZpvp7IZtfIgpZT-mA8qa7B'
	access_params['redirect_uri'] = cs['redirect_uri']
	access_params['grant_type'] =  'authorization_code'
	params =  urllib.urlencode(access_params)
	url_access_token = 'https://accounts.google.com/o/oauth2/token' 
	req = urllib2.Request(url_access_token, params) #Post request
	
	response = urllib2.urlopen(req)
	
	access_token = ast.literal_eval(response.read())
	
	'''
	 Get access Token JSON in following formAT AND SAVE IN THE FILE
	{
	  "access_token":"1/fFAGRNJru1FTz70BzhT3Zg",
	  "expires_in":3920,
	  "token_type":"Bearer"
	}	
	'''
	file = open('/home/jatin/Github/scraping/access_token.json','w')
	file.write(str(access_token))
	
	
	response_body = test_html % url_access_token 

	status = '200 OK'
	
	response_headers = [
						('Content-Type','text/html'),
						('Content-Length', str(len(response_body)))
	                   ]
	start_response(status, response_headers)
	return [response_body]
						
def application(environ, start_response):
	if environ['PATH_INFO'] == '/':
		return index(environ,start_response)
	elif environ['PATH_INFO'] == '/oauth2callback':
		return login(environ, start_response)
HOST = 'ubuntu'
httpd =  make_server('192.168.48.128',8051,application)
print "Serving the port on 8051"
httpd.serve_forever()
