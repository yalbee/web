from requests import get, post, delete

token = post('http://webyl.herokuapp.com/api/login', json={'email': 'aaaa@q', 'password': 'ee'}).json()
print(token)
print(get('http://webyl.herokuapp.com/api/comments', headers={'Authorization': token['token']}).json())
print(post('http://webyl.herokuapp.com/api/comments', headers={'Authorization': token['token']},
           json={'new_id': 1, 'content': 'fassafafs'}).json())
print(post('http://webyl.herokuapp.com/api/comments', headers={'Authorization': token['token']},
           json={'new_id': 999, 'content': 'fassafafs'}).json())
print(post('http://webyl.herokuapp.com/api/comments', headers={'Authorization': token['token']},
           json={'new_id': 'a', 'content': 'fassafafs'}).json())
print(get('http://webyl.herokuapp.com/api/comments/1', headers={'Authorization': token['token']}).json())
print(delete('http://webyl.herokuapp.com/api/comments/1', headers={'Authorization': token['token']}).json())
print(delete('http://webyl.herokuapp.com/api/comments/999', headers={'Authorization': token['token']}).json())
print(delete('http://webyl.herokuapp.com/api/comments/a', headers={'Authorization': token['token']}).json())
print(get('http://webyl.herokuapp.com/api/comments', headers={'Authorization': token['token']}).json())
