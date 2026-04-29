import requests,json

with open('sample_payload.json') as f:
 payload=json.load(f)

r=requests.post(
'http://127.0.0.1:8000/analyze',
json=payload
)

print(r.json())
