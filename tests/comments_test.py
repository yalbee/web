from requests import get, post, delete

token = post('http://127.0.0.1:8080/api/login', json={'email': 'aaaa@q', 'password': 'ee'}).json()
print(token)
print(get('http://127.0.0.1:8080/api/comments', headers={'Authorization': token['token']}).json())
print(post('http://127.0.0.1:8080/api/comments', headers={'Authorization': token['token']},
           json={'new_id': 1, 'content': 'fassafafs'}).json())
print(post('http://127.0.0.1:8080/api/comments', headers={'Authorization': token['token']},
           json={'new_id': 999, 'content': 'fassafafs'}).json())
print(post('http://127.0.0.1:8080/api/comments', headers={'Authorization': token['token']},
           json={'new_id': 'a', 'content': 'fassafafs'}).json())
print(get('http://127.0.0.1:8080/api/comments/1', headers={'Authorization': token['token']}).json())
print(delete('http://127.0.0.1:8080/api/comments/1', headers={'Authorization': token['token']}).json())
print(delete('http://127.0.0.1:8080/api/comments/999', headers={'Authorization': token['token']}).json())
print(delete('http://127.0.0.1:8080/api/comments/a', headers={'Authorization': token['token']}).json())
print(get('http://127.0.0.1:8080/api/comments', headers={'Authorization': token['token']}).json())
