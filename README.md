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

## Heroku

This is mildly sketchy.  This is a python project and you use the python buildpack for it.  However, to calculate outdated dependencies for Mozilla Accounts I need the `yarn` command to exist.  Heroku will install it for me if it thinks I'm running a Node project, so, I have an empty `package.json` and `yarn.lock` file in the root and have told Heroku to run the `nodejs` builpack before the `python` one:

```
heroku buildpacks:add --index 1 heroku/nodejs
```

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
