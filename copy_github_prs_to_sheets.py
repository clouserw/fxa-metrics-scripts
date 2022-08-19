import re
import os
import time
from datetime import datetime
import urllib3

import gspread
from github import Github

# Sometimes people will put something like this in the comment:
#     Closes: https://github.com/mozilla/fxa/issues/8423

# re.compile('[Cc]lose(s|d)?:?\s?(https:\/\/github\.com\/[A-Za-z\/_-]*|#)?\d+'),
expressions = [re.compile('[Ff]ix(ed|es)?:?\s?FXA-\d+'),
               re.compile('[Cc]lose(s|d)?:?\s?FXA-\d+'),
               re.compile('[Rr]esolve(s|d)?:?\s?FXA-\d+')]

# This isn't a perfect system because we have to parse the first comment.  Don't rely on these results for anything but approximation.
# TODO: Don't use this.  these are paired to JIRA now.  We should be looking there.
def pr_has_an_issue(pr):

    try:
        for expression in expressions:
            if pr.body:
                if expression.search(pr.body):
                    return True
            if pr.title:
                if expression.search(pr.title):
                    return True
    except Exception as e:
        print(f" {pr.number}  Error {e}")

    return False

g = Github(os.environ.get('GITHUB_KEY'), retry=urllib3.util.retry.Retry(total=10, status_forcelist = (500, 502, 504), backoff_factor = 0.3))

repo = g.get_repo(os.environ.get('GITHUB_REPO'))

pulls = repo.get_pulls(state='all', sort='created', direction='desc')

export = [['id', 'number', 'url', 'title', 'state', 'author', 'created_at', 'updated_at', 'closed_at', 'merged_at', 'draft', 'time_to_close', 'reviewers', 'has_an_issue', 'time_to_merge']]

_open = 0
_closed = 0

for i in pulls:

    _closed_at = ""
    _updated_at = ""
    _merged_at = ""
    _time_to_close = ""
    _time_to_merge = ""
    _reviewers = ""

    if i.updated_at:
        _updated_at = i.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    if i.closed_at:
        _closed_at = i.closed_at.strftime('%Y-%m-%d %H:%M:%S')
        _time_to_close = (i.closed_at - i.created_at).total_seconds()
        _closed += 1
    else:
        _open += 1
    if i.merged_at:
        _merged_at = i.merged_at.strftime('%Y-%m-%d %H:%M:%S')
        _time_to_merge = (i.merged_at - i.created_at).total_seconds()

    # This is actual reviewers, not just requested.  This includes all review states (eg. they might have rejected the patch).  This also doesn't deduplicate names if a person participates more than once.
    reviews = i.get_reviews()
    _reviewers = ', '.join([str(review.user.login) for review in reviews])

    _has_an_issue = pr_has_an_issue(i)

    _row = [i.id,
            i.number,
            i.html_url,
            i.title,
            i.state,
            i.user.login,
            i.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            _updated_at,
            _closed_at,
            _merged_at,
            i.draft,
            _time_to_close,
            _reviewers,
            _has_an_issue,
            _time_to_merge
    ]

    export.append(_row)

    _rate_limit = g.get_rate_limit()
    _rate_limit_reset = (_rate_limit.core.reset - datetime.utcnow()).seconds /60

    #print(f"Used: Core ({_rate_limit.core.remaining}/{_rate_limit.core.limit}) Resets in {_rate_limit_reset:.1f} min")
    if _rate_limit.core.remaining < 2:
        _seconds = (_rate_limit.core.reset - datetime.utcnow()).seconds + 5
        #print(f"Hit rate limit.  Sleeping for: {_seconds} seconds")
        time.sleep(_seconds)
    #print(f"Used: Search ({_rate_limit.search.remaining}/{_rate_limit.search.limit}) Resets {_rate_limit.search.reset.strftime('%H:%M:%S')}")

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

wks = sh.worksheet('Pull Request Data')
wks.clear()
wks.update('A1', export)

wks = sh.worksheet('Counts')
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
wks.append_row([now, 'prs','open',_open], value_input_option="USER_ENTERED", table_range='A1')
wks.append_row([now, 'prs','closed',_closed], value_input_option="USER_ENTERED", table_range='A1')
