import requests

URL = 'http://localhost:8000/api-auth/login/?next=/api/v1/'


client = requests.session()

# Retrieve the CSRF token first
client.get(URL)  # sets cookie
if 'csrftoken' in client.cookies:
    # Django 1.6 and up
    csrftoken = client.cookies['csrftoken']
else:
    # older versions
    csrftoken = client.cookies['csrf']
USERNAME = 'aaron'
PASSWORD = 'rm7gisnh'
login_data = dict(username=USERNAME, password=PASSWORD, csrfmiddlewaretoken=csrftoken, next='/')
r = client.post(URL, data=login_data, headers=dict(Referer=URL))
rsp = client.get('http://localhost:8000/api/v1/')