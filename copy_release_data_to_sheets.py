import datetime
import os
import requests

import gspread

credentials = {
    "type": "service_account",
    "project_id": os.environ.get('GSPREAD_PROJECT_ID'),
    "private_key_id": os.environ.get('GSPREAD_PRIVATE_KEY_ID'),
    "private_key": os.environ.get('GSPREAD_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.environ.get('GSPREAD_CLIENT_EMAIL'),
    "client_id": os.environ.get('GSPREAD_CLIENT_ID'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ.get('GSPREAD_CLIENT_X509_CERT_URL')
}

gc = gspread.service_account_from_dict(credentials)
sh = gc.open_by_key(os.environ.get('SPREADSHEET_KEY'))

wks = sh.worksheet('Tag Data')

# doesn't include customs or admin, which aren't available on the net
servers = [
            'accounts.firefox.com',
            'api.accounts.firefox.com',
            'oauth.accounts.firefox.com',
            'profile.accounts.firefox.com',
            'subscriptions.firefox.com',
            'eventbroker-prod.fxa.prod.cloudops.mozgcp.net'
            ]

export = [['timestamp', 'server', 'version', 'commit', 'reason', 'notes']]

for server in servers:

    _data = requests.get(f"https://{server}/__version__").json()

    try:
        # This might already contain the data (ie. no updates since this script last ran)
        _candidate_cell = wks.find(server)
        _candidate_row = wks.row_values(_candidate_cell.row)

        #print(_candidate_row)

        if _candidate_row[2] == _data['version']:
            #print(f"{_data['version']} already exists: {_candidate_row}")
            continue
    except (AttributeError, gspread.exceptions.CellNotFound) as e:
        pass

    #print(_data)
    _row = [
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        server,
        _data.get('version',''),
        _data.get('commit',''),
        _data.get('l10n',''),
        _data.get('tospp','')
    ]

    wks.insert_row(values=_row, index=2, value_input_option="USER_ENTERED")
