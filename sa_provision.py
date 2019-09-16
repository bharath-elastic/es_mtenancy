import json
import requests
from getpass import getpass
import yaml
import argparse
from csv import DictReader
from pprint import pprint


ES_HEADERS = {'Content-Type': 'application/json'}
KIBANA_HEADERS = {'kbn-xsrf': 'true', 'Content-Type': 'application/json'}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', help='action to take',
                        choices={'create', 'delete'}, default='create')
    parser.add_argument('-c', '--config', help='config file',
                        default='config.yaml')
    parser.add_argument('-p', '--provision', help='provisioning file',
                        default='prov.csv')
    return parser.parse_args()


def get_config(filename):
    with open(filename, 'r') as cf:
        return yaml.safe_load(cf)


def get_provision(filename):
    with open(filename, 'r') as pf:
        d = DictReader(pf)
        return [doc for doc in d]


def get_role_model(role):
    model = requests.get(ENDPOINTS['role']
                         + role, headers=ES_HEADERS,
                         auth=CREDS, timeout=TIMEOUT).json()
    return model[role]


def get_config(conf_file):
    with open(conf_file, 'r') as cf:
        return yaml.safe_load(cf)


def get_creds(user):
    return (user, getpass(f'enter password for {user} :'))


def get_endpoints(url):
    endpoints = {'space': url['kibana'] + '/api/spaces/space',
                 'user': url['es'] + '/_security/user/',
                 'role': url['es'] + '/_security/role/'}
    return endpoints


def create_space(space_name):
    data = {'id': space_name, 'name': space_name,
            'initials': space_name[-2:]}
    res = requests.post(ENDPOINTS['space'],
                        headers=KIBANA_HEADERS, data=json.dumps(data),
                        timeout=TIMEOUT, auth=CREDS)
    print(res.status_code)
    return res


def create_role(row):
    model = get_role_model(row['role_model'])
    model['applications'][0]['resources'] = [f"space:{row['space_name']}"]
    role_endpoint = ENDPOINTS['role'] + row['role_name']
    res = requests.put(role_endpoint,
                       headers=ES_HEADERS, data=json.dumps(model),
                       timeout=TIMEOUT, auth=CREDS)
    print(res.status_code)
    return res


def create_user(row):
    user_name, _,role_name, _, pwd = row.values()
    print(row)
    print(user_name, role_name, pwd)
    user_doc = {'password': pwd, 'roles': [role_name]}
    user_endpoint = ENDPOINTS['user'] + user_name
    res = requests.post(user_endpoint,
                        headers=ES_HEADERS,
                        data=json.dumps(user_doc),
                        auth=CREDS)
    print(res.status_code)
    pprint(res.json(), compact=True)
    return res


def delete_role(role_name):
    role_endpoint = ENDPOINTS['role'] + role_name
    res = requests.delete(role_endpoint, auth=CREDS)
    print(res.status_code)
#    pprint(res.json())
    return res


def delete_space(space_name):
    res = requests.delete(ENDPOINTS['space'] + f'/{space_name}',
                          headers=KIBANA_HEADERS,
                          timeout=TIMEOUT, auth=CREDS)
    print(res.status_code)
#    pprint(res.json(), compact=True)
    return res


def delete_user(user_name):
    del_user_endpoint = ENDPOINTS['user'] + user_name
    res = requests.delete(del_user_endpoint,
                          timeout=TIMEOUT, auth=CREDS)
    return res


def delete_setup():
    for row in get_provision(ARGS.provision):
        delete_role(row['role_name'])
        delete_space(row['space_name'])
        delete_user(row['user_name'])


def create_setup():
    for row in get_provision(ARGS.provision):
        create_space(row['space_name'])
        create_role(row)
        create_user(row)


def main():
    if ARGS.action == 'delete':
        delete_setup()
    elif ARGS.action == 'create':
        create_setup()


ARGS = parse_args()
TIMEOUT = 30
CONFIG = get_config(ARGS.config)
ENDPOINTS = get_endpoints(CONFIG['url'])
CREDS = get_creds(CONFIG['auth']['user'])
main()
