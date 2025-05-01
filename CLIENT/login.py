import requests

while True:
    usrname = input("Enter Username: ")
    passwd = input("Enter Password: ")

    data = {
        "username": usrname,
        "password": passwd
    }

    res = requests.post("http://127.0.0.1:8000/login/", json = data)
    print(res.json() )