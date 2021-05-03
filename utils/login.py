import requests
from bs4 import BeautifulSoup as bs
from getpass import getpass


def login(url):
    session = requests.session()
    username = input("Enter Username: ")
    password = getpass("Enter Password: ")
    # password = input("Enter Password: ")
    payload = {
        'name': username,
        'pass': password
    }
    r = session.get(url)
    soup = bs(r.content, "lxml")
    tag = soup.find_all(attrs={"name": "form_build_id"})
    payload['form_build_id'] = tag[0]['value']
    payload['form_id'] = "user_login_form"
    payload["op"] = "SIGN+IN"
    r = session.post(url, data=payload)
    return session


def updateHeader(session):
    session.headers.update(
        {"uid": session.cookies['uid'], "token": session.cookies['token']})
    return session
