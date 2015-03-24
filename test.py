import urllib
import ast
f = open("/home/jatin/Github/scraping/client_secrets.json",'r')
SECRETS = f.read()
SECRETS =  ast.literal_eval(SECRETS)
print SECRETS["web"]
print urllib.urlencode(SECRETS["web"])
