from urllib.parse import urlencode
from urllib.request import Request, urlopen

url = '192.168.178.156' 
post_fields = {'test': 'data'}  

request = Request(url, urlencode(post_fields).encode())
json = urlopen(request).read()
print(json)
