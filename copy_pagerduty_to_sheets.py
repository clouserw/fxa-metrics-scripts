import datetime
import os
import sys

import gspread
from pdpyras import APISession

if not "PAGERDUTY_TOKEN" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

session = APISession(os.environ.get("PAGERDUTY_TOKEN"))

# API is limited to 6 months
since = datetime.date.today() - datetime.timedelta(179)
today = datetime.date.today()

# lol at this API
params = {"service_ids[]": 'PSDDIR0',
          'since': since.strftime("%Y-%m-%d"),
          'until': today.strftime("%Y-%m-%d")
}

incidents = session.list_all('incidents', params=params)

export = [['incident_number', 'title', 'description', 'created_at', 'last_status_change_at', 'status', 'urgency', 'self', 'minutes_to_resolve']]

for i in incidents:

    # datastudio surprisngly bad...
    _created = datetime.datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    _fixed   = datetime.datetime.strptime(i['last_status_change_at'], '%Y-%m-%dT%H:%M:%SZ')
    _time    = _fixed - _created


    _row = [i['incident_number'],
            i['title'],
            i['description'],
            i['created_at'].replace('T', ' ').replace('Z',''),
            i['last_status_change_at'].replace('T', ' ').replace('Z',''),
            i['status'],
            i['urgency'],
            i['self'],
            _time.total_seconds() / 60
    ]

    export.append(_row)

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

wks = sh.worksheet('Pagerduty Data')
wks.clear()
wks.update('A1', export, raw=False)
