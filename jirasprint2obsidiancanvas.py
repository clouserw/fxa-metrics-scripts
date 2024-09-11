# This will query jira (Note: hardcoded to board 225 - change that if you're actually using this script) for a sprint with the name of the first argument passed to the script.  Output is to stdout (which I redirect to a file).  
# Example usage:
# python jirasprint2obsidiancanvas.py "FxA Train 291" > FXA\ Train\ 291.canvas
#
# @author Wil Clouser

import argparse
import datetime
import json
import os
import random
import sys
import time

import gspread

from jira import JIRA

if not "JIRA_EMAIL" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

if not "JIRA_TOKEN" in os.environ:
    print("Please set environment variables")
    sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process JIRA sprints.")
    parser.add_argument("sprint_name", type=str, help="Name of the sprint to process")
    return parser.parse_args()

def generate_random_hex_id():
    return ''.join(random.choices('0123456789abcdef', k=16))

args = parse_arguments()
sprint_name = args.sprint_name

jira = JIRA(basic_auth=(os.environ.get('JIRA_EMAIL'),
                        os.environ.get('JIRA_TOKEN')),
            server="https://mozilla-hub.atlassian.net")

# It's wild there is no way to query the API by name.  This is a huge waste, but here we are. :weary:
chunk = 50
index = 0
sprint = {}
while True:
    startAt = index * chunk
    _sprints = jira.sprints(board_id=225, startAt=startAt, maxResults=chunk)
    if len(_sprints):
        for i in _sprints:
            if i.name == sprint_name:
                sprint = i
                break
        index += 1
    else:
        break

if not sprint:
    print(f"Sprint {sprint_name} not found.")
    sys.exit(1)

# Parse sprint start date
sprint_start_date = datetime.datetime.strptime(sprint.startDate.split('.')[0], '%Y-%m-%dT%H:%M:%S')

chunk = 50
index = 0
issues = []
while True:
    startAt = index * chunk
    _issues = jira.search_issues(f'project = "FXA" AND sprint={sprint.id} ORDER BY created DESC', startAt=startAt, maxResults=chunk)

    if len(_issues):
        for i in _issues:
            issues.append(i)
        index += 1
    else:
        break

# New code to format issues into JSON
nodes = []
x_coordinate = 0
for issue in issues:
    _created = datetime.datetime.strptime(issue.fields.created.split('.')[0], '%Y-%m-%dT%H:%M:%S')

    _type=""
    if issue.fields.issuetype.name == "Bug":
        _type="🪲"
    
    color = "2" if _created > sprint_start_date else "5"

    node = {
        "id": generate_random_hex_id(),
        "type": "text",
        "text": f"{_type} {issue.key} - {issue.fields.summary}",
        "x": x_coordinate,
        "y": 0,
        "width": 250,
        "height": 60,
        "color": color
    }
    nodes.append(node)
    x_coordinate += 20

d = sprint_start_date
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 1 - {d.strftime('%b %d')}\n{sprint_name} starts", "x": -500, "y": -720, "width": 250, "height": 60})
d += datetime.timedelta(days=1)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 2 - {d.strftime('%b %d')}", "x": -220, "y": -720, "width": 250, "height": 60})
d += datetime.timedelta(days=1)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 3 - {d.strftime('%b %d')}", "x": 60, "y": -720, "width": 250, "height": 60})
d += datetime.timedelta(days=3)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 4 - {d.strftime('%b %d')}", "x": 340, "y": -720, "width": 250, "height": 60})
d += datetime.timedelta(days=1)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 5 - {d.strftime('%b %d')}", "x": 620, "y": -720, "width": 250, "height": 60})
d += datetime.timedelta(days=1)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 6 - {d.strftime('%b %d')}", "x": -500, "y": -120, "width": 250, "height": 60})
d += datetime.timedelta(days=1)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 7 - {d.strftime('%b %d')}", "x": -220, "y": -120, "width": 250, "height": 60})
d += datetime.timedelta(days=1)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 8 - {d.strftime('%b %d')}", "x": 60, "y": -120, "width": 250, "height": 60})
d += datetime.timedelta(days=3)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 9 - {d.strftime('%b %d')}", "x": 340, "y": -120, "width": 250, "height": 60})
d += datetime.timedelta(days=1)
nodes.append({"id": generate_random_hex_id(), "type": "text", "text": f"DAY 10 - {d.strftime('%b %d')}", "x": 620, "y": -120, "width": 250, "height": 60})

output = {"nodes": nodes}
print(json.dumps(output, indent=4))