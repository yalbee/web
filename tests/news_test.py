from requests import get, post, delete, put

token = post('http://webyl.herokuapp.com/api/login', json={'email': 'aaaa@q', 'password': 'ee'}).json()
print(token)
print(get('http://webyl.herokuapp.com/api/news', headers={'Authorization': token['token']}).json())
print(get('http://webyl.herokuapp.com/api/news/1', headers={'Authorization': token['token']}).json())
print(get('http://webyl.herokuapp.com/api/news/999', headers={'Authorization': token['token']}).json())
print(get('http://webyl.herokuapp.com/api/news/a', headers={'Authorization': token['token']}).json())
print(post('http://webyl.herokuapp.com/api/news', headers={'Authorization': token['token']}, json={
    'title': 'eeeee',
    'category': 'IT',
    'content': 'aasscacs'}).json())
print(post('http://webyl.herokuapp.com/api/news', headers={'Authorization': token['token']}, json={
    'title': 'eeeee',
    'category': 'AXAX',
    'content': 'aasscacs'}).json())
print(get('http://webyl.herokuapp.com/api/news', headers={'Authorization': token['token']}).json())
print(put('http://webyl.herokuapp.com/api/news/2', headers={'Authorization': token['token']}, json={
    'title': 'fassafsafasf',
    'category': 'Спорт',
    'content': 'пыввппвывп'}).json())
print(put('http://webyl.herokuapp.com/api/news/2', headers={'Authorization': token['token']}, json={
    'title': 'fassafsafasf',
    'category': 'Спорт'}).json())
print(get('http://webyl.herokuapp.com/api/news', headers={'Authorization': token['token']}).json())
print(delete('http://webyl.herokuapp.com/api/news/1', headers={'Authorization': token['token']}).json())
print(delete('http://webyl.herokuapp.com/api/news/2', headers={'Authorization': token['token']}).json())
print(get('http://webyl.herokuapp.com/api/news', headers={'Authorization': token['token']}).json())
