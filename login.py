import requests
import json
import firebase_admin.exceptions
import os
from google.api_core import exceptions


def login():
    url = "https://identitysso.betfair.com/api/login"
    payload = 'username=' + os.environ.get('BF_LOGIN') + '&password=' + os.environ.get('BF_PASS')
    headers = {'X-Application': 'squads',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'
               }

    resp = requests.post(url, data=payload, headers=headers)
    js = resp.json()
    print(js)
    status = js['status']
    token = ''
    if status == "SUCCESS":
        token = js['token']

    return token


def get_or_create_token(db):
    # Token creation and retrieval
    doc_ref = db.collection(u'tokens').document(u'token')
    try:
        token_obj = doc_ref.get()
        token = token_obj.to_dict()['value']
        print("firestore {}".format(token))
        if token == "":
            token = create_token_betfair()
            doc_ref.set({'value': token})

    except (exceptions.ResourceExhausted, TypeError):
        token = create_token_betfair()
        doc_ref.set({'value': token})

    return token


def delete_token(db):
    doc_ref = db.collection(u'tokens').document(u'token')
    doc_ref.delete()


def create_token_betfair():
    token = login()
    print("betfair {}".format(token))

    return token


