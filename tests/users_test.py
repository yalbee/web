from requests import get, post

print(post('http://127.0.0.1:8080/api/register', json={'email': 'axax@a', 'password': 'ee',
                                                       'name': 'a', 'surname': 'b',
                                                       'hometown': 'll', 'about': 'lol',
                                                       'birthday': '05/05/2005'}).json())
print(get('http://127.0.0.1:8080/api/users').json())
print(get('http://127.0.0.1:8080/api/users/1').json())
