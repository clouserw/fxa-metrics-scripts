import datetime
import os
import requests
import sys

import gspread

if not "BUGZILLA_KEY" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

if not "SPREADSHEET_KEY" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

try:

    total = 0
    sec_none_total = 0
    sec_low_total = 0
    sec_mod_total = 0
    sec_high_total = 0
    sec_crit_total = 0

    r = requests.get('https://bugzilla.mozilla.org/rest/bug',
                    params={'api_key': os.environ.get('BUGZILLA_KEY'),
                            'resolution': '---',
                            'component': 'Server: Firefox Accounts',
                            'product': 'Cloud Services',
                            'f1': 'bug_group', 'o1': 'equals', 'v1': 'cloud-services-security'
                            })

    for bug in r.json()['bugs']:
        total = total + 1

    r = requests.get('https://bugzilla.mozilla.org/rest/bug',
                    params={'api_key': os.environ.get('BUGZILLA_KEY'),
                            'resolution': '---',
                            'component': 'Server: Firefox Accounts',
                            'product': 'Cloud Services',
                            'f1': 'bug_group', 'o1': 'equals', 'v1': 'cloud-services-security',
                            'f2': 'keywords', 'o2': 'substring', 'v2': 'sec-low'
                            })

    for bug in r.json()['bugs']:
        sec_low_total = sec_low_total + 1

    r = requests.get('https://bugzilla.mozilla.org/rest/bug',
                    params={'api_key': os.environ.get('BUGZILLA_KEY'),
                            'resolution': '---',
                            'component': 'Server: Firefox Accounts',
                            'product': 'Cloud Services',
                            'f1': 'bug_group', 'o1': 'equals', 'v1': 'cloud-services-security',
                            'f2': 'keywords', 'o2': 'substring', 'v2': 'sec-moderate'
                            })

    for bug in r.json()['bugs']:
        sec_mod_total = sec_mod_total + 1

    r = requests.get('https://bugzilla.mozilla.org/rest/bug',
                    params={'api_key': os.environ.get('BUGZILLA_KEY'),
                            'resolution': '---',
                            'component': 'Server: Firefox Accounts',
                            'product': 'Cloud Services',
                            'f1': 'bug_group', 'o1': 'equals', 'v1': 'cloud-services-security',
                            'f2': 'keywords', 'o2': 'substring', 'v2': 'sec-high'
                            })

    for bug in r.json()['bugs']:
        sec_high_total = sec_high_total + 1

    r = requests.get('https://bugzilla.mozilla.org/rest/bug',
                    params={'api_key': os.environ.get('BUGZILLA_KEY'),
                            'resolution': '---',
                            'component': 'Server: Firefox Accounts',
                            'product': 'Cloud Services',
                            'f1': 'bug_group', 'o1': 'equals', 'v1': 'cloud-services-security',
                            'f2': 'keywords', 'o2': 'substring', 'v2': 'sec-critical'
                            })

    for bug in r.json()['bugs']:
        sec_crit_total = sec_crit_total + 1


    # sec-none isn't an official thing
    sec_none_total = total - sec_low_total - sec_mod_total - sec_high_total

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

wks = sh.worksheet('Counts2')
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
wks.append_row([now, 'security issues', 'open', total], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'no-sec-score', 'open', sec_none_total], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'sec-low', 'open', sec_low_total], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'sec-moderate', 'open', sec_mod_total], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'sec-high', 'open', sec_high_total], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'sec-critical', 'open', sec_crit_total], value_input_option="USER_ENTERED", table_range='A1')
