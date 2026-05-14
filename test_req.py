import requests

session = requests.Session()

# register
print("Registering...")
resp = session.post('http://127.0.0.1:5000/auth/register', data={
    'username': 'newuser1',
    'email': 'new1@example.com',
    'password': 'password123'
})
print("Register Status:", resp.status_code)

# login
print("Logging in...")
resp = session.post('http://127.0.0.1:5000/auth/login', data={
    'email': 'new1@example.com',
    'password': 'password123'
})
print("Login Status:", resp.status_code)
# check if redirected to dashboard
print("Current URL:", resp.url)
print("Text snippet:", resp.text[-200:])
