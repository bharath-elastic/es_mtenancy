import json
import requests
from getpass import getpass
import yaml
import argparse
from csv import DictReader


ES_HEADERS = {'Content-Type': 'application/json'}
KIBANA_HEADERS = {'kbn-xsrf': 'true', 'Content-Type': 'application/json'}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tear-down', action='store_true',
                        help='tear down existing setup')
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
    print(f'creating space {space_name}', end='...')
    res = requests.post(ENDPOINTS['space'],
                        headers=KIBANA_HEADERS, data=json.dumps(data),
                        timeout=TIMEOUT, auth=CREDS)
    if res.status_code == 200:
        print('OK')
    else:
        print(res.json())
    return res


def create_role(row):
    model = get_role_model(row['role_model'])
    model['applications'][0]['resources'] = [f"space:{row['space_name']}"]
    role_endpoint = ENDPOINTS['role'] + row['role_name']
    print(f"creating role {row['role_name']}", end='...')
    res = requests.put(role_endpoint,
                       headers=ES_HEADERS, data=json.dumps(model),
                       timeout=TIMEOUT, auth=CREDS)
    if res.status_code == 200:
        print('OK')
    else:
        print(res.json())
    return res


def create_user(row):
    user_name, _,role_name, _, pwd = row.values()
    #print(row)
    #print(user_name, role_name, pwd)
    user_doc = {'password': pwd, 'roles': [role_name]}
    user_endpoint = ENDPOINTS['user'] + user_name
    print(f"creating user {row['user_name']}", end='...')
    res = requests.post(user_endpoint,
                        headers=ES_HEADERS,
                        data=json.dumps(user_doc),
                        auth=CREDS)
    if res.status_code == 200:
        print('OK')
    else:
        print(res.json())
    return res


def delete_role(role_name):
    role_endpoint = ENDPOINTS['role'] + role_name
    print(f'deleting role {role_name}', end='...')
    res = requests.delete(role_endpoint, auth=CREDS)
    if res.status_code == 200:
        print('OK')
    else:
        print(res.json())
    return res


def delete_space(space_name):
    print(f'deleting space {space_name}', end='...')
    res = requests.delete(ENDPOINTS['space'] + f'/{space_name}',
                          headers=KIBANA_HEADERS,
                          timeout=TIMEOUT, auth=CREDS)
    if res.status_code == 204:
        print('OK')
    else:
        print(res.json())
    return res


def delete_user(user_name):
    del_user_endpoint = ENDPOINTS['user'] + user_name
    print(f'delete user {user_name}', end='...')
    res = requests.delete(del_user_endpoint,
                          timeout=TIMEOUT, auth=CREDS)
    if res.status_code == 200:
        print('OK')
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
    if ARGS.tear_down:
        delete_setup()
    else:
        create_setup()


ARGS = parse_args()
TIMEOUT = 30
CONFIG = get_config(ARGS.config)
ENDPOINTS = get_endpoints(CONFIG['url'])
CREDS = get_creds(CONFIG['auth']['user'])
main()
