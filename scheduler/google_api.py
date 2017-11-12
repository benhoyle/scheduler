# -*- coding: utf-8 -*-

import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from scheduler.models import Task, TimePeriod

import pytz
from datetime import datetime
from dateutil import parser

# The paths for the .json credential files are stored in a private.py file
try:
    from private import (
        CLIENT_SECRET_FILE, CAL_CREDS_FILENAME, SHEET_CREDS_FILENAME,
        CAL_ID, SHEET_ID,  OUTPUT_CAL_ID
    )
except ImportError:
    CLIENT_SECRET_FILE = ""
    CAL_CREDS_FILENAME = ""
    SHEET_CREDS_FILENAME = ""
    CAL_ID = ""
    SHEET_ID = ""
    OUTPUT_CAL_ID = ""


CAL_SCOPES = 'https://www.googleapis.com/auth/calendar'
SHEET_SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
APP_NAME = 'scheduler'


def get_credentials(filename, scopes):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = Storage(filename)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scopes)
        flow.user_agent = APP_NAME
        credentials = tools.run_flow(flow, store, flags=None)
        print('Storing credentials to ' + filename)
    return credentials


def get_tasks_from_sheet(sheet_id=SHEET_ID):
    """ Get a list of tasks from Google Sheet. """
    credentials = get_credentials(SHEET_CREDS_FILENAME, SHEET_SCOPES)
    http = credentials.authorize(httplib2.Http())
    discovery_url = (
        'https://sheets.googleapis.com/$discovery/rest?'
        'version=v4'
    )
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discovery_url)

    range_name = 'Todo!A1:F'
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    tasks = []
    for value in values[1:]:
        try:
            tasks.append(
                Task(
                    value[4],
                    value[3],
                    taskref=value[0],
                    tasktype=value[1],
                    description=value[2],
                    timetype="hours"
                    )
                )
        except:
            continue
    return tasks


def post_assigned_time(events, calendar_id=OUTPUT_CAL_ID):
    """ Add events to output calendar.

    Each event is a dict in the following format:
    event = {
      'summary': 'Google I/O 2015',
      'location': '800 Howard St., San Francisco, CA 94103',
      'description': 'A chance to hear more.',
      'start': {
        'dateTime': '2015-05-28T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'dateTime': '2015-05-28T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      }
    }"""
    credentials = get_credentials(CAL_CREDS_FILENAME, CAL_SCOPES)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    output_events = list()
    for event in events:
        output_events.append(
            service.events().insert(
                calendarId=OUTPUT_CAL_ID, body=event
            ).execute()
        )
    return output_events


def get_work_blocks(calendar_id=CAL_ID):
    """ Gets free work blocks as defined in a Google calendar."""
    credentials = get_credentials(CAL_CREDS_FILENAME, CAL_SCOPES)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId=calendar_id, timeMin=now, maxResults=30, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    time_periods = []
    for event in events:
        # Create a new time period object
        # First deal with timezones
        start_timezone = pytz.timezone(event['start']['timeZone'])
        end_timezone = pytz.timezone(event['start']['timeZone'])
        # Convert UTC times into timezone aware times
        startdt = parser.parse(event['start']['dateTime']) \
            .replace(tzinfo=pytz.utc).astimezone(start_timezone)
        enddt = parser.parse(event['end']['dateTime']) \
            .replace(tzinfo=pytz.utc).astimezone(end_timezone)
        time_periods.append(TimePeriod(startdt, enddt))
    return time_periods


def get_all_events(calendar_id):
    """ Get all events from a calendar."""
    credentials = get_credentials(CAL_CREDS_FILENAME, CAL_SCOPES)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    all_events = list()
    page_token = None
    while True:
        event_results = service.events().list(
            calendarId=calendar_id, pageToken=page_token
            ).execute()
        events = event_results.get('items', [])
        all_events = all_events + events
        page_token = event_results.get('nextPageToken')
        if not page_token:
            break
    return all_events


def clear_events(calendar_id=OUTPUT_CAL_ID):
    """ Wipe all events from a particular calendar."""
    # Get all events
    events = get_all_events(calendar_id)
    # Iterate through and delete all events
    credentials = get_credentials(CAL_CREDS_FILENAME, CAL_SCOPES)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    for event in events:
        service.events().delete(
            calendarId=calendar_id, eventId=event['id']
            ).execute()
