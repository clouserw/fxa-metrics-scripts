import datetime
import os

import gspread
from jira import JIRA

if not "JIRA_EMAIL" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

if not "JIRA_TOKEN" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

if not "SPREADSHEET_KEY" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

jira = JIRA(basic_auth=(os.environ.get('JIRA_EMAIL'),
                        os.environ.get('JIRA_TOKEN')),
            server="https://mozilla-hub.atlassian.net")

chunk = 100 # Appears to be the max for the API...
index = 0
issues = []
while True:
    startAt = index * chunk
    #_issues = jira.search_issues('project=FXA and created > startOfDay(-5) order by id desc', startAt=startAt, maxResults=chunk)
    _issues = jira.search_issues('project=FXA order by id desc', startAt=startAt, maxResults=chunk)
    #print(f"startat: {startAt} len: {len(_issues)}")
    if len(_issues):
        for i in _issues:
            issues.append(i)
        index += 1
    else:
        break

_closed = 0
_open = 0

export = [['key',
           'permalink',
           'id',
           'assignee',
           'created',
           'found in',
           'issuetype',
           'reporter',
           'resolution',
           'resolutiondate',
           'status',
           'storypoints',
           'summary',
           'updated',
           'epic',
           'originalstorypoints',
           'timetoresolve',
           'severity',
           'priority',
           'labels']]

for issue in issues:
    try:
        # Assignee
        _assignee = ''
        if issue.fields.assignee:
            if issue.fields.assignee.emailAddress:
                _assignee = issue.fields.assignee.emailAddress

        # Found In
        if issue.fields.customfield_10217:
            _found_in = issue.fields.customfield_10217.value
        else:
            _found_in = ''

        # Resolution
        if issue.fields.resolution:
            _resolution = issue.fields.resolution.name
        else:
            _resolution = ''

        # Story Points
        if issue.fields.customfield_10037:
            _story_points = issue.fields.customfield_10037
        else:
            _story_points = ''

        # Original Story Points
        if issue.fields.customfield_10310:
            _original_story_points = issue.fields.customfield_10310
        else:
            _original_story_points = ''

        # Severity
        if issue.fields.customfield_10319:
            _severity = issue.fields.customfield_10319.value
        else:
            _severity = ''

        # Labels
        _labels = ', '.join(issue.fields.labels)



        # Fix jira's ridiculous date to something reasonable. Jira dates come in like this 2022-01-11T16:35:33.833-0500
        _created = datetime.datetime.strptime(issue.fields.created.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        _updated = datetime.datetime.strptime(issue.fields.updated.split('.')[0], '%Y-%m-%dT%H:%M:%S')

        if issue.fields.resolutiondate:
            _resolutiondate = datetime.datetime.strptime(issue.fields.resolutiondate.split('.')[0], '%Y-%m-%dT%H:%M:%S')
            _resolutiondate_string = _resolutiondate.strftime('%Y-%m-%d %H:%M:%S')
            _time_to_resolve = (_resolutiondate - _created).total_seconds()
            _closed +=1
        else:
            _resolutiondate_string = ''
            _time_to_resolve = ''
            _open +=1

        _row = [issue.key,
                issue.permalink(),
                issue.id,
                _assignee,
                _created.strftime('%Y-%m-%d %H:%M:%S'),
                _found_in,
                issue.fields.issuetype.name,
                issue.fields.reporter.emailAddress,
                _resolution,
                _resolutiondate_string,
                issue.fields.status.name,
                _story_points,
                issue.fields.summary,
                _updated.strftime('%Y-%m-%d %H:%M:%S'),
                issue.fields.customfield_10014,
                _original_story_points,
                _time_to_resolve,
                _severity,
                issue.fields.priority.id,
                _labels
        ]

        export.append(_row)
    except Exception as e:
        # exceptions started getting thrown with the move to atlassian host.
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

wks = sh.worksheet('Issue Data')
wks.clear()
# Setting raw to false allows dates to be interpreted as dates
wks.update('A1', export, raw=False)

wks = sh.worksheet('Counts')
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
wks.append_row([now, 'issues','open',_open], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'issues','closed',_closed], value_input_option="USER_ENTERED", table_range='A1')
