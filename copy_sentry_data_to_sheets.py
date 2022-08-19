import datetime
import os
import requests
import sys

import gspread

# This script is useless in its current state.  Sentry.io doesn't have a
# /stats/ API endpoint anymore, so, this will need to be reworked

if not "SENTRY_TOKEN" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

headers = {"Authorization": f"Bearer {os.environ.get('SENTRY_TOKEN')}"}

start = datetime.date.today() - datetime.timedelta(90)
today = datetime.date.today()
params = {"stat": "", "resolution": "1d", "since": start.strftime("%s"), "until": today.strftime("%s")}

projects = [
            'fxa-admin-panel-prod',
            'fxa-auth-customs-prod',
            'fxa-auth-prod',
            'fxa-content-client-prod',
            'fxa-content-server-prod',
            'fxa-event-broker-prod',
            'fxa-payments-prod',
            'fxa-profile-prod',
            'fxa-support-panel-prod'
            ]

export = [['timestamp', 'received', 'generated', 'blacklisted', 'rejected', 'project']]

for project in projects:

    endpoint = f"https://sentry.prod.mozaws.net/api/0/projects/operations/{project}/stats/"

    params["stat"] = "received"
    _received = requests.get(endpoint, params=params, headers=headers).json()
    params["stat"] = "generated"
    _generated = requests.get(endpoint, params=params, headers=headers).json()
    params["stat"] = "blacklisted"
    _blacklisted = requests.get(endpoint, params=params, headers=headers).json()
    params["stat"] = "rejected"
    _rejected = requests.get(endpoint, params=params, headers=headers).json()

    # This might be sketchy, because it assumes all these dates line up for each request, but they did in my tests, so....
    for a,b,c,d in zip(_received, _generated, _blacklisted, _rejected):
        t = datetime.datetime.utcfromtimestamp(a[0])
        export.append([t.strftime("%Y-%m-%d %H:%M:%S"), a[1], b[1], c[1], d[1], project])

#for i in export:
  #print(i)


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

wks = sh.worksheet('Sentry Data')
wks.clear()
wks.update('A1', export, raw=False)
