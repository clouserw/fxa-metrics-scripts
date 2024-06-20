import datetime
import os
import requests
import sys

import gspread

if not "GITHUB_KEY" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

# Sorry for hardcoding, but I'm not going to make all of these env vars
repositories = ["mozilla/fxa",
                "mozilla/fxa-content-server-l10n",
                "mozilla/ecosystem-platform",
                "mozilla/eslint-plugin-fxa",
                "mozilla/fxa-pairing-channel",
                "mozilla/mozlog",
                "mozilla/pyfxa",
                "mozilla/restmail.net",
                "mozilla/node-client-sessions",
                "mozilla/node-convict",
                "mozilla/grunt-l10n-lint",
                "mozilla/browserid-local-verify",
                "mozilla-fxa/chosen",
                "mozilla-fxa/node-uap",
                "mozilla-fxa/grunt-po2json",
                ]

try:
    # pygithub doesn't support the dependabot API so have to do this ourselves
    headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {os.environ.get('GITHUB_KEY')}"}

    totals = {}

    for i in repositories:
        # Max per page is 100.  I don't have time to do pagination.  If we're over 100 maybe that's another problem?
        url = f"https://api.github.com/repos/{i}/dependabot/alerts?state=open&per_page=100"

        r = requests.get(url, headers=headers).json()

        if (r) :
            totals[i] = len(r)
        else:
            totals[i] = 0


except Exception as e:
    print(f"Caught exception: {e}")

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

wks = sh.worksheet('Counts')
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
for i in totals:
    wks.append_row([now, f'dependabot {i} security issues', 'open', totals[i]], value_input_option="USER_ENTERED", table_range='A1')
