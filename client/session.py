from requests import Session
import json


with open('conf.json', encoding='utf-8') as f:
    conf = json.loads(f.read())


session = Session()

session.head(conf['SERVER_ADDRESS'])


def get_session():
    return session
