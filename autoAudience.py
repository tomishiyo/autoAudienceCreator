import re
from typing import Tuple, List, Union

import requests

from sfmc_classes import Folder, DataExtension


def read_credentials() -> Tuple[str, str, str]:
    """
    Read file credentials.txt for SFMC API related information
    :return: client_id (str), client_secret (str), api_domain (str)
    """
    with open('credentials.txt', 'r') as file:
        lines = file.readlines()

        client_id = lines[1].strip()
        client_secret = lines[3].strip()
        api_domain = lines[5].strip()
        return client_id, client_secret, api_domain


def read_inputs() -> Tuple[str, str, int]:
    """
    Read file inputs.txt for inputs values pertinent to the campaign.
    :return: de_parent_folder_id, campaign_code, language_versions
    """
    with open('inputs.txt', 'r') as file:
        lines = file.readlines()

        de_parent_folder_id = lines[1].strip()
        campaign_code = lines[3].strip()
        language_versions = lines[5].strip()

        return de_parent_folder_id, campaign_code, int(language_versions)


def get_oauth_token():
    """
    Authenticates within SFMC API via a GET request to a REST endpoint
    :return: access_token
    :rtype: str
    """
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


def generate_payload(structure_type, parent_folder_id, name, **kwargs):
    """
    Generates XML payloads to be sent to the SOAP api endpoint
    :param structure_type: folder, de or qa_de. Specifies the type of the object.
    :type structure_type: str
    :param parent_folder_id: The parent folder identifier.
    :type parent_folder_id: str
    :param name: The email's campaign name.
    :type name: str
    :param kwargs: is_sendable - flag to specify if the DE is sendable or not. Defaults to false.
    :return: The XML payload to be sent via a POST request to the SOAP endpoint.
    :rtype: str
    """
    file_name = 'payloads/'
    if structure_type == 'folder':
        file_name += 'folder_'
    elif structure_type == 'qa_de':
        file_name += 'qa_'
    file_name += 'de_payload.xml'

    with open(file_name, 'r') as file:
        unparsed_xml = file.read()
        xml = re.sub(r'SUBDOMAIN', api_domain, unparsed_xml)
        xml = re.sub(r'OAUTH_TOKEN', oauth_token, xml)

        if structure_type == 'folder':
            xml = re.sub(r'PARENT_FOLDER_ID', str(parent_folder_id), xml)
            xml = re.sub(r'DE_FOLDER_NAME', name, xml)
        elif structure_type == 'de' or structure_type == 'qa_de':
            xml = re.sub(r'DE_NAME', name, xml)
            xml = re.sub(r'FOLDER_ID', str(parent_folder_id), xml)

            is_sendable_arg = kwargs.get('is_sendable', False)
            is_sendable = 'true' if is_sendable_arg else 'false'

            xml = re.sub(r'SENDABLE_STATUS', is_sendable, xml)

    return xml


def create_object(structure_type, name, parent_folder_id, **kwargs) -> Union[Folder, DataExtension, None]:
    """
    Creates either data extensions or folders via SOAP calls.

    If the call is unsuccessful, function returns None.
    :param structure_type: de, qa_de or folder. Specifies the object type.
    :type structure_type: str
    :param name: The email's campaign name.
    :type name: str
    :param parent_folder_id: The parent folder on which the object will be created.
    :type parent_folder_id: str
    :param kwargs: is_sendable - flag to specify if the DE is sendable or not. Defaults to false.
    :return: The created object
    """
    headers = {
        'Content-Type': 'text/xml; charset=utf-8'
    }

    payload = generate_payload(structure_type, parent_folder_id, name, **kwargs)

    try:
        response = requests.request('POST', soap_url, headers=headers, data=payload)
        if response.status_code == 200:
            if structure_type == 'folder':
                object_id = re.search(r'<NewID>(\d*)</NewID>', response.text).group(1)
                response_object = Folder(object_id, parent_folder_id)
            elif structure_type == 'de' or structure_type == 'qa_de':
                object_id = re.search(r'<ObjectID>(.*)<\/ObjectID>', response.text).group(1)
                response_object = DataExtension(object_id, parent_folder_id)

            return response_object
        else:
            print(f'Creation request failed with HTTP code {response.status_code}')

    except Exception as error:
        print(f'Unexpected error at function create_object: {error}')


def create_campaign_des(parent_folder_id) -> Union[List, None]:
    """
    Create staging, send and QA data extension at the campaign folder.

    Returns None if call fails or if language codes are not 1 or 2.
    :param parent_folder_id: The folder ID on which the DEs will be created.
    :type parent_folder_id: str
    :return: A list containing the created data extensions
    """
    if language_versions == 2:
        languages = ['-EN', '-ES']
    elif language_versions == 1:
        languages = ['']
    else:
        raise NotImplementedError('Unsupported number of language versions')

    staging_des = []
    send_des = []

    for lang in languages:
        staging_de_name = campaign_code + '_STAGE' + lang
        send_de_name = campaign_code + '_SEND' + lang

        staging_des.append(create_object('de', staging_de_name, parent_folder_id, is_sendable=False))
        send_des.append(create_object('de', send_de_name, parent_folder_id, is_sendable=True))

    qa_de_name = campaign_code + '_QA'
    qa_de = create_object('qa_de', qa_de_name, parent_folder_id, is_sendable=True)

    if staging_des and send_des and qa_de:
        return staging_des, send_des, qa_de


def main():
    print(f'Creating DE folder for campaign {campaign_code} with parent folder {parent_folder_de_id}...')
    de_folder = create_object('folder', campaign_code, parent_folder_de_id)

    if de_folder:
        print(f'Folder for {campaign_code} created successfully, it was assigned ID {de_folder.id_code}!')
        staging_des, send_des, qa_de = create_campaign_des(de_folder.id_code)
        print('Staging, sends and QA data extensions created successfully!')
    else:
        print('There was an unexpected error creating the DE folder...')
        print('Aborting')
        return 1


if __name__ == '__main__':
    # API definitions and credentials
    client_id, client_secret, api_domain = read_credentials()
    # End points
    # wsdl_url = f'https://{api_domain}.soap.marketingcloudapis.com/etframework.wsdl'
    auth_url = f'https://{api_domain}.auth.marketingcloudapis.com/v2/token'
    soap_url = f'https://{api_domain}.soap.marketingcloudapis.com/Service.asmx'
    # Input readings
    parent_folder_de_id, campaign_code, language_versions = read_inputs()

    print('Authenticating...')
    oauth_token = get_oauth_token()

    if oauth_token:
        print('Authentication successfull!')
        main()
    else:
        print('Authentication unsucessfull')
        print('Exiting...')

