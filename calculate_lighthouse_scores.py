# Note this requires Node's lighthouse:
#     $ npm install -g lighthouse

import datetime
import os

import gspread

from lighthouse import LighthouseRunner

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

TIMINGS = ['accessability', 'speed-index']
ADDITIONAL_SETTINGS = ['--no-enable-error-reporting', '--only-categories=performance,accessibility,seo,best-practices']

endpoints = [
    'https://accounts.firefox.com'
]

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
for endpoint in endpoints:
    report = LighthouseRunner(endpoint, form_factor='desktop', additional_settings=ADDITIONAL_SETTINGS, timings=TIMINGS, quiet=False).report

    audits = report.audits(0) # the "zero" means everything is passing.  woo

    _all_the_rows = [
        [now, endpoint, 'performance', 'overall', report.score['performance'], report.score['performance']],
        [now, endpoint, 'accessibility', 'overall', report.score['accessibility'], report.score['accessibility']],
        [now, endpoint, 'seo', 'overall', report.score['seo'], report.score['seo']],
        [now, endpoint, 'best-practices', 'overall', report.score['best-practices'], report.score['best-practices']],
    ]

    performance_audits = audits.get('performance')
    if performance_audits:
        for audit in performance_audits.passed:
            #print(f"ID: {audit.id}, Score: {audit.score}, NumVal: {audit.numval}")
            _row = [now, endpoint, 'performance', audit.id, audit.score, audit.numval]
            _all_the_rows.append(_row)

    a11y_audits = audits.get('accessibility')
    if a11y_audits:
        for audit in a11y_audits.passed:
            #print(f"ID: {audit.id}, Score: {audit.score}, NumVal: {audit.numval}")
            _row = [now, endpoint, 'accessibility', audit.id, audit.score, audit.numval]
            _all_the_rows.append(_row)

    bp_audits = audits.get('best-practices')
    if bp_audits:
        for audit in bp_audits.passed:
            #print(f"ID: {audit.id}, Score: {audit.score}, NumVal: {audit.numval}")
            _row = [now, endpoint, 'best-practices', audit.id, audit.score, audit.numval]
            _all_the_rows.append(_row)

    seo_audits = audits.get('seo')
    if seo_audits:
        for audit in seo_audits.passed:
            #print(f"ID: {audit.id}, Score: {audit.score}, NumVal: {audit.numval}")
            _row = [now, endpoint, 'seo', audit.id, audit.score, audit.numval]
            _all_the_rows.append(_row)

wks = sh.worksheet('Lighthouse')
wks.append_rows(_all_the_rows, value_input_option="USER_ENTERED")