import requests
from sfmc_classes import Folder
from zeep import Client, Settings


def read_credentials():
    with open('credentials.txt', 'r') as file:
        lines = file.readlines()

        client_id = lines[1].strip()
        client_secret = lines[3].strip()
        api_domain = lines[5].strip()
        return client_id, client_secret, api_domain


def read_inputs():
    with open('inputs.txt', 'r') as file:
        lines = file.readlines()

        de_parent_folder_id = lines[1].strip()

        return de_parent_folder_id


def get_oauth_token(client_id, client_secret, url):
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        request = requests.post(url, json=payload)
        if request.status_code == 200:
            return request.json()['access_token']
        else:
            print(f'get_o_auth_token: An HTTP error code {request.status_code} was raised.')
    except Exception as error:
        print(f'An exception has occurred: {error}')


if __name__ == '__main__':
    client_id, client_secret, api_domain = read_credentials()
    auth_url = f'https://{api_domain}.auth.marketingcloudapis.com/v2/token'
    wsdl_url = f'https://{api_domain}.soap.marketingcloudapis.com/etframework.wsdl'
    soap_url = f'https://{api_domain}.soap.marketingcloudapis.com/Service.asmx'

    de_parent_folder_id = read_inputs()

    oauth_token = get_oauth_token(client_id, client_secret, auth_url)

    soap_client = Client(wsdl_url)
