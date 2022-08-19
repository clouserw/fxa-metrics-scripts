import datetime
import os
import sys

import gspread
from jira import JIRA

if not "SPREADSHEET_KEY" in os.environ:
    print("Please set environment variables")
    sys.exit(1)


jira = JIRA(server="https://mozilla-hub.atlassian.net")

chunk = 100 # Appears to be the max for the API...
index = 0
issues = []
while True:
    startAt = index * chunk
    _issues = jira.search_issues('project=FXA and labels in (maintenance) and resolution is empty and (component not in ("Subscription Platform") or component is empty)', startAt=startAt, maxResults=chunk)
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


gc = gspread.oauth()
sh = gc.open_by_key(os.environ.get('SPREADSHEET_KEY'))

wks = sh.worksheet('Counts2')
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
wks.append_row([now, 'maintenance points', '', total_story_points], value_input_option="USER_ENTERED")
wks.append_row([now, 'maintenance issues', '', len(issues)], value_input_option="USER_ENTERED")
wks.append_row([now, 'maintenance issues with no points', '', total_issues_with_no_points], value_input_option="USER_ENTERED")
