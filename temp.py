from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

main_html = """
<html>
<head><title> Welcome to redirection test page </title> </head>
<body>
	<form method="get" action='/visit'>
		<input type=radio name='site' value=google> Google
		<input type=radio name='site' value=facebook> Facebook
		<input type=submit value=submit>
	</form>
</body>
</html>
"""


def main(environ, start_response):

	response_body = main_html
	print type(response_body)	
	status = '200 OK'
	
	response_headers = [
						('Content-Type','text/html'),
						('Content-Length', str(len(response_body)))
	                   ]
	
						
	start_response(status, response_headers)
	return [response_body]


def visit(environ, start_response):
	qs = parse_qs(environ['QUERY_STRING'])
	dest = qs.ge('site')[0]
	if dest == 'google':
		start_response('301 Moved Permanently', [('Location','http://google.com')])
	else:
		start_response('301 Moved Permanently', [('Location','http://facebook.com')])

	return [1]


def app(environ, start_response):
	if environ['PATH_INFO'] == '/':
		return main(environ, start_response)
	elif environ['PATH_INFO'] == '/visit':
		return visit(environ, start_response)

httpd =  make_server('192.168.48.128',8052, app)
print 'Serving on port 8052'
httpd.serve_forever()
	
