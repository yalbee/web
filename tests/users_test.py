from requests import get, post

token = post('http://webyl.herokuapp.com/api/login', json={'email': 'aaaa@q', 'password': 'ee'}).json()
print(token)
print(get('http://webyl.herokuapp.com/api/users', headers={'Authorization': token['token']}).json())
print(get('http://webyl.herokuapp.com/api/users/3', headers={'Authorization': token['token']}).json())
print(get('http://webyl.herokuapp.com/api/users/999', headers={'Authorization': token['token']}).json())
print(get('http://webyl.herokuapp.com/api/users/a', headers={'Authorization': token['token']}).json())
