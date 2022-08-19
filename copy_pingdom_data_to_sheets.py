import datetime
import requests
import os
import sys

import gspread

if not "PINGDOM_TOKEN" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

headers = {"Authorization": f"Bearer {os.environ.get('PINGDOM_TOKEN')}"}

start = datetime.date.today() - datetime.timedelta(90)
today = datetime.date.today()
params = {"resolution": "day", "includeuptime": "true", "from": start.strftime("%s")}

projects = {'Content Server': '1826088',
            'Auth Server': '1826075',
            'Profile Server': '1826083',
            'OAuth Server': '1826082',
            'Event Broker': '5496442',
            'Payments Server': '5496447'}

export = [['avgresponse', 'downtime', 'starttime', 'unmonitored', 'uptime', 'project', 'fuzzy_uptime_percent', 'unmonitored_percent']]

for project in projects:

    endpoint = f"https://api.pingdom.com/api/3.1/summary.performance/{projects[project]}"

    _stats = requests.get(endpoint, params=params, headers=headers).json()

    for i in _stats['summary']['days']:
        t = datetime.datetime.utcfromtimestamp(i['starttime'])
        try:
            _fup = (i['uptime']/(i['downtime']+i['unmonitored']+i['uptime']))*100
            _um = (i['unmonitored']/(i['downtime']+i['unmonitored']+i['uptime']))*100
        except ZeroDivisionError:
            _fup = 0
            _um = 0
        export.append([i['avgresponse'], i['downtime'], t.strftime("%Y-%m-%d %H:%M:%S"), i['unmonitored'], i['uptime'], project, _fup, _um])

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

wks = sh.worksheet('Pingdom Data')
wks.clear()
wks.update('A1', export, raw=False)
