import requests
import re
from sfmc_classes import Folder


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
        campaign_code = lines[3].strip()

        return de_parent_folder_id, campaign_code


def get_oauth_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        request = requests.post(auth_url, json=payload)
        if request.status_code == 200:
            return request.json()['access_token']
        else:
            print(f'get_o_auth_token: An HTTP error code {request.status_code} was raised.')
    except Exception as error:
        print(f'An exception has occurred: {error}')


def generate_xml_de_folder(parent_folder_id, name):
    with open('folder_de_payload.xml', 'r') as file:
        unparsed_xml = file.read()
        xml = re.sub(r'SUBDOMAIN', api_domain, unparsed_xml)
        xml = re.sub(r'OAUTH_TOKEN', oauth_token, xml)
        xml = re.sub(r'DE_FOLDER_NAME', name, xml)
        xml = re.sub(r'PARENT_FOLDER_ID', str(parent_folder_id), xml)

        return xml


def create_de_folder():
    payload = generate_xml_de_folder(parent_folder_de_id, campaign_code)
    headers = {
        'Content-Type': 'text/xml; charset=utf-8'
    }
    try:
        response = requests.request('POST', soap_url, headers=headers, data=payload)

        if response.status_code == 200:
            folder_id = re.search(r'<NewID>(\d*)</NewID>', response.text).group(1)
            de_folder = Folder(folder_id, parent_folder_de_id)

            return de_folder
        else:
            print(f'The folder creation was unsuccessfull with status code {response.status_code}')
    except Exception as error:
        print(f'Unexpected error at function create_de_folder: {error}')


def main():
    print(f'Creating DE folder for campaign {campaign_code} with parent folder {parent_folder_de_id}...')
    de_folder = create_de_folder()

    if de_folder:
        print(f'Folder for {campaign_code} created successfully, it was assigned ID {de_folder.id_code}!')


if __name__ == '__main__':
    client_id, client_secret, api_domain = read_credentials()

    # wsdl_url = f'https://{api_domain}.soap.marketingcloudapis.com/etframework.wsdl'
    auth_url = f'https://{api_domain}.auth.marketingcloudapis.com/v2/token'
    soap_url = f'https://{api_domain}.soap.marketingcloudapis.com/Service.asmx'

    parent_folder_de_id, campaign_code = read_inputs()



    print('Authenticating...')
    oauth_token = get_oauth_token()

    if oauth_token:
        print('Authentication successfull!')
        main()
    else:
        print('Authentication unsucessfull')
        print('Exiting...')

