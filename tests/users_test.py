from requests import get, post

token = post('http://127.0.0.1:8080/api/login', json={'email': 'bruh@bruh', 'password': 'ee'}).json()
print(token)
print(get('http://127.0.0.1:8080/api/users', headers={'Authorization': token['token']}).json())
print(get('http://127.0.0.1:8080/api/users/3', headers={'Authorization': token['token']}).json())
print(get('http://127.0.0.1:8080/api/users/999', headers={'Authorization': token['token']}).json())
print(get('http://127.0.0.1:8080/api/users/a', headers={'Authorization': token['token']}).json())
