import datetime
import os
import sys

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
    _issues = jira.search_issues('project=FXA and labels in (maintenance) and type in (task,story,bug) and resolution is empty and (component not in ("Subscription Platform") or component is empty)', startAt=startAt, maxResults=chunk)
    #print(f"startat: {startAt} len: {len(_issues)}")
    if len(_issues):
        for i in _issues:
            issues.append(i)
        index += 1
    else:
        break

total_story_points = 0
total_issues_with_no_points = 0

for issue in issues:
    try:
        # Story Points
        if issue.fields.customfield_10037:
            _story_points = issue.fields.customfield_10037
        else:
            _story_points = 0
            total_issues_with_no_points = total_issues_with_no_points + 1

        total_story_points = total_story_points + _story_points

    except Exception as e:
        # exceptions started getting thrown with the move to atlassian host.
        # Haven't had time to debug...There are usually ~<10
        print(f"Caught exception: {e}")

# More effecient to do a single query and iterate through it, but I'm writing
# this while in a meeting and copy/paste is easier
index = 0
non_maintenance_issues = []
while True:
    startAt = index * chunk
    _issues = jira.search_issues('project=FXA and (labels is EMPTY or labels not in (maintenance)) and type in (task,story) and resolution is empty and (component not in ("Subscription Platform") or component is empty)', startAt=startAt, maxResults=chunk)
    #print(f"startat: {startAt} len: {len(_issues)}")
    if len(_issues):
        for i in _issues:
            non_maintenance_issues.append(i)
        index += 1
    else:
        break

non_maintenance_non_bug_story_points = 0
non_maintenance_non_bug_issues_with_no_points = 0

for issue in non_maintenance_issues:
    try:
        # Story Points
        if issue.fields.customfield_10037:
            _story_points = issue.fields.customfield_10037
        else:
            _story_points = 0
            non_maintenance_non_bug_issues_with_no_points = non_maintenance_non_bug_issues_with_no_points + 1

        non_maintenance_non_bug_story_points = non_maintenance_non_bug_story_points + _story_points

    except Exception as e:
        # exceptions started getting thrown with the move to atlassian host.
        # Haven't had time to debug...There are usually ~<10
        print(f"Caught exception: {e}")

# More effecient to do a single query and iterate through it, but I'm writing
# this while in a meeting and copy/paste is easier
index = 0
non_maintenance_bugs = []
while True:
    startAt = index * chunk
    _issues = jira.search_issues('project=FXA and (labels is empty or labels not in (maintenance)) and type in (bug) and resolution is empty and (component not in ("Subscription Platform") or component is empty)', startAt=startAt, maxResults=chunk)
    #print(f"startat: {startAt} len: {len(_issues)}")
    if len(_issues):
        for i in _issues:
            non_maintenance_bugs.append(i)
        index += 1
    else:
        break

non_maintenance_bug_story_points = 0
non_maintenance_bugs_with_no_points = 0

for issue in non_maintenance_bugs:
    try:
        # Story Points
        if issue.fields.customfield_10037:
            _story_points = issue.fields.customfield_10037
        else:
            _story_points = 0
            non_maintenance_bugs_with_no_points = non_maintenance_bugs_with_no_points + 1

        non_maintenance_bug_story_points = non_maintenance_bug_story_points + _story_points

    except Exception as e:
        # exceptions started getting thrown with the move to atlassian host.
        # Haven't had time to debug...There are usually ~<10
        print(f"Caught exception: {e}")



# If you send maxResults=0 to the Jira API you only get a small json back with the total in it.  I suspect the python-jira library is replacing those results with it's own heavy query but I don't have time to dig into it now.  That may also mean this is susceptible to the 100 issue return limit of the API, but I'm not going to test that right now.  Edit: I got a result of 197 back, so, looks like it's not or the API limit went up.

_ret = jira.search_issues('project=FXA and (labels in (maintenance) AND labels in (oauth)) and resolution is empty and (component not in ("Subscription Platform") or component is empty) order by created asc', startAt=0, maxResults=0)
maintenance_issues_cat_oauth = len(_ret)

_ret = jira.search_issues('project=FXA and (labels in (maintenance) AND labels in (dependencies)) and resolution is empty and (component not in ("Subscription Platform") or component is empty) order by created asc', startAt=0, maxResults=0)
maintenance_issues_cat_dependencies = len(_ret)

_ret = jira.search_issues('project=FXA and (labels in (maintenance) AND labels in (sentry)) and resolution is empty and (component not in ("Subscription Platform") or component is empty) order by created asc', startAt=0, maxResults=0)
maintenance_issues_cat_sentry = len(_ret)

_ret = jira.search_issues('project=FXA and (labels in (maintenance) AND labels not in (dependencies,oauth,sentry)) and resolution is empty and (component not in ("Subscription Platform") or component is empty) order by created asc', startAt=0, maxResults=0)
maintenance_issues_cat_other = len(_ret)

_ret = jira.search_issues('project=FXA and (labels in (needsproduct)) and resolution is empty and (component not in ("Subscription Platform") or component is empty) order by created asc', startAt=0, maxResults=0)
issues_needs_product = len(_ret)

_ret = jira.search_issues('project=FXA and (labels in (needsux)) and resolution is empty and (component not in ("Subscription Platform") or component is empty) order by created asc', startAt=0, maxResults=0)
issues_needs_ux = len(_ret)



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
wks.append_row([now, 'maintenance points', '', total_story_points], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'maintenance issues', '', len(issues)], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'maintenance issues with no points', '', total_issues_with_no_points], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'non-maintenance task points', '', non_maintenance_non_bug_story_points], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'non-maintenance tasks', '', len(non_maintenance_issues)], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'non-maintenance tasks with no points', '', non_maintenance_non_bug_issues_with_no_points], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'non-maintenance bug points', '', non_maintenance_bug_story_points], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'non-maintenance bugs', '', len(non_maintenance_bugs)], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'non-maintenance bugs with no points', '', non_maintenance_bugs_with_no_points], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'maintenance_issues_cat_oauth', '', maintenance_issues_cat_oauth], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'maintenance_issues_cat_dependencies', '', maintenance_issues_cat_dependencies], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'maintenance_issues_cat_sentry', '', maintenance_issues_cat_sentry], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'maintenance_issues_cat_other', '', maintenance_issues_cat_other], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'issues_needs_product', '', issues_needs_product], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'issues_needs_ux', '', issues_needs_ux], value_input_option="USER_ENTERED", table_range='A1')

