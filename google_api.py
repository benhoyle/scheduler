# -*- coding: utf-8 -*-

import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

from private import (
    CLIENT_SECRET_FILE, CAL_CREDS_FILENAME, SHEET_CREDS_FILENAME,
    CAL_ID, SHEET_ID
)

CAL_SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
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
    return values


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
    return events
