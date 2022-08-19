import os

import gspread
from influxdb import InfluxDBClient


client = InfluxDBClient(os.environ.get('INFLUX_HOST'),
                        port=os.environ.get('INFLUX_PORT'),
                        username=os.environ.get('INFLUX_USER'),
                        password=os.environ.get('INFLUX_PASS'),
                        database=os.environ.get('INFLUX_DB'),
                        ssl=True, verify_ssl=True)

data = client.query('select first(*) from "fxa-auth-server.url_request" WHERE "path"=\'v1_account\' AND time >=now() - 24h GROUP BY time(2m)')

export = [['time',
           '50_percentile',
           '95_percentile',
           '99_percentile',
           'path']]

for row in data.get_points():
    _row = [row['time'],
            row['first_50_percentile'],
            row['first_95_percentile'],
            row['first_99_percentile']
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
wks = sh.worksheet('Auth Server Timing')
wks.clear()

wks.update('A1', export)
