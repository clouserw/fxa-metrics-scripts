import datetime
import json
import os
import subprocess
import sys

from git import Repo
import gspread
from jira import JIRA

if not "SPREADSHEET_KEY" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

targetdir = "/tmp/fxacheckout"

if not os.path.isdir(targetdir):
  Repo.clone_from("https://github.com/mozilla/fxa.git", targetdir)

repo = Repo(targetdir)
repo.remotes.origin.pull()

os.chdir(targetdir)

workspaces = {
'fxa',
'123done',
'db-migrations',
'fortress',
'functional-tests',
'fxa-admin-panel',
'fxa-admin-server',
'fxa-auth-client',
'fxa-auth-server',
'fxa-content-server',
'fxa-customs-server',
'fxa-dev-launcher',
'fxa-event-broker',
'fxa-geodb',
'fxa-graphql-api',
'fxa-payments-server',
'fxa-profile-server',
'fxa-react',
'fxa-settings',
'fxa-shared',
}

results = {}

for workspace in workspaces:
    results[workspace] = {'dependencies': 0, 'devdependencies': 0, 'total': 0}
    cmd = ['yarn', 'workspace', workspace, 'outdated', '--json']
    res = subprocess.run(cmd, capture_output=True, text=True)

    try:
        if not res.stdout.strip():
            print(f"No output from yarn for workspace: {workspace}")
            continue

        r = json.loads(res.stdout)
        for pkg in r:
            pkg_type = pkg.get('type')
            if pkg_type == 'dependencies':
                results[workspace]['dependencies'] += 1
            elif pkg_type == 'devDependencies':
                results[workspace]['devdependencies'] += 1

        results[workspace]['total'] = (
            results[workspace]['dependencies'] +
            results[workspace]['devdependencies']
        )
    except Exception as e:
        print(f"Failed to process workspace '{workspace}': {e}")


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
for i in results:
    wks.append_rows([[now, f"{i} outdated dependencies", '', results[i]['dependencies']],
                     [now, f"{i} outdated devdependencies", '', results[i]['devdependencies']],
                     [now, f"{i} outdated dependencies total", '', results[i]['total']]],
                    value_input_option="USER_ENTERED", table_range='A1')
