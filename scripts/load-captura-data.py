import requests
import os
from faker import Faker

# Get domain from env.
DOMAIN = os.environ.get('DOMAIN')
fake = Faker()

# TODO: Figure out how to import captura data.
# For now, generate random data.
scientist_list = list()
for _ in range(10):
    scientist_list.append({
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'ci': str(fake.pyint(min_value=1000000, max_value=9999999)),
    })

# Get token and do requests with it.
token_request = requests.post(f'{DOMAIN}api/get-user-token/', json={'username': 'superuser', 'password': 'superuser'})
token = token_request.json()['token']
auth_header = {'Authorization': f'Bearer {token}'}
for scientist in scientist_list:
    scientist_request = requests.post(f'{DOMAIN}api/scientist/', json=scientist, headers=auth_header)

# Finally, get list of all scientists
r = requests.get(f'{DOMAIN}api/scientist/', headers=auth_header)
print(r.json())
