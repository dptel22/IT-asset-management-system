import requests

s = requests.Session()
r = s.post('http://localhost:3000/login', data={'username':'emp1', 'password':'password123', 'role':'employee'})
if r.status_code == 200:
    res = s.get('http://localhost:3000/employee/asset-requests/status')
    print("Asset Requests Status:", res.status_code, res.text)
    res2 = s.get('http://localhost:3000/employee/transfer-requests/status')
    print("Transfer Requests Status:", res2.status_code, res2.text)
else:
    print("Login failed", r.status_code)
