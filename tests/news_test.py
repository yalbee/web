from requests import get, post, delete, put

token = post('http://127.0.0.1:8080/api/login', json={'email': 'aaaa@q', 'password': 'ee'}).json()
print(token)
print(get('http://127.0.0.1:8080/api/news', headers={'Authorization': token['token']}).json())
print(get('http://127.0.0.1:8080/api/news/1', headers={'Authorization': token['token']}).json())
print(get('http://127.0.0.1:8080/api/news/999', headers={'Authorization': token['token']}).json())
print(get('http://127.0.0.1:8080/api/news/a', headers={'Authorization': token['token']}).json())
print(post('http://127.0.0.1:8080/api/news', headers={'Authorization': token['token']}, json={
    'title': 'eeeee',
    'category': 'IT',
    'content': 'aasscacs'}).json())
print(post('http://127.0.0.1:8080/api/news', headers={'Authorization': token['token']}, json={
    'title': 'eeeee',
    'category': 'AXAX',
    'content': 'aasscacs'}).json())
print(get('http://127.0.0.1:8080/api/news', headers={'Authorization': token['token']}).json())
print(put('http://127.0.0.1:8080/api/news/2', headers={'Authorization': token['token']}, json={
    'title': 'fassafsafasf',
    'category': 'Спорт',
    'content': 'пыввппвывп'}).json())
print(put('http://127.0.0.1:8080/api/news/2', headers={'Authorization': token['token']}, json={
    'title': 'fassafsafasf',
    'category': 'Спорт'}).json())
print(get('http://127.0.0.1:8080/api/news', headers={'Authorization': token['token']}).json())
print(delete('http://127.0.0.1:8080/api/news/1', headers={'Authorization': token['token']}).json())
print(delete('http://127.0.0.1:8080/api/news/2', headers={'Authorization': token['token']}).json())
print(get('http://127.0.0.1:8080/api/news', headers={'Authorization': token['token']}).json())
