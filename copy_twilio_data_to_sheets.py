import datetime
import os
import sys

import gspread

from twilio.rest import Client

if not "TWILIO_ACCOUNT_SID" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

if not "TWILIO_AUTH_TOKEN" in os.environ:
    print("Please set environment variables")
    sys.exit(1)


account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

yesterday = client.usage.records.yesterday.list()

_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

_export = []

for record in yesterday:
    if record.price > 0:
        _row = [_date,
                record.category,
                record.count,
                float(record.usage),
                record.usage_unit,
                float(record.price),
                record.price_unit,
                record.description
        ]
        _export.append(_row)
        print(_row)

if not _export:
    sys.exit(1)

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

wks = sh.worksheet('Twilio')
wks.append_rows(_export, value_input_option="USER_ENTERED")