# fxa-metrics-scripts
Simple scripts for compiling FxA metrics


These scripts are most useful as an _example_ of how to pull from APIs.  To use
the scripts directly you'd need to have Jira custom fields with the same IDs,
spreadsheets with the same columns, etc.  Just go into this knowing you'll need
to adjust the scripts.

Additionally, there aren't a lot of guardrails or error checking...




# Using these scripts

## Configuration

I pass configuration into the scripts using environment variables.  Fill in the
values in `local.env` and source it into your environment before running the
scripts.
1. `pip install -r requirements.txt`
2. `cp local.env-dist local.env`
3. `source local.env`
4. `python <script>`



## Scheduling

To run a cron job from a virtualenv:

```
* * * * * /path/to/virtualenv/bin/python /path/to/fxa-metrics-scripts/copy_jira_data_to_sheets.py
```

To run a cron job with specific environment variables within a virtualenv:

```
* * * * * . /path/to/fxa-metrics-scripts/local.env; /path/to/virtualenv/bin/python /path/to/fxa-metrics-scripts/copy_jira_data_to_sheets.py
```

To run from heroku use the scheduling add-on with commands like `python
<script>.py`
