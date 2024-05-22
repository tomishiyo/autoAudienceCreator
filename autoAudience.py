def read_credentials():
    with open('credentials.txt', 'r') as file:
        lines = file.readlines()

        client_id = lines[1].strip()
        client_secret = lines[3].strip()
        api_domain = lines[5].strip()
        return client_id, client_secret, api_domain


if __name__ == '__main__':
    read_credentials()