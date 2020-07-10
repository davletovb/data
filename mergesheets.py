from __future__ import print_function

import os.path
import pickle
from time import sleep

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
APPLICATION_NAME = "Google Sheets API Python"

SPREADSHEET_ID = "ID"


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            flow.user_agent = APPLICATION_NAME
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    sheets = [
        "ID"
    ]
    results = []

    for sh in sheets:
        values = get_sheet(sheet, sh)
        results.extend(values)

    #sheet_name = "Sheet1"
    #start_row = 2
    #end_row = len(results)
    merged = pd.DataFrame(results,
                          columns=['COLUMN'])

    #save_to_sheet(sheet, sheet_name + "!A" + str(start_row) + ":P" + str(end_row), results)
    merged.to_csv("merged.csv", header=True, index=False)

def get_sheet(sheet, spreadsheet):
    sleep(10)
    start_row = 2
    sheet_name, end_row = get_range(sheet, spreadsheet)
    working_range = sheet_name + "!A" + str(start_row) + ":P" + str(end_row)
    result = sheet.values().get(spreadsheetId=spreadsheet, range=working_range).execute()
    values = result.get('values', [])
    return values


def get_range(sheet, spreadsheet):
    sleep(10)
    result = sheet.get(spreadsheetId=spreadsheet,
                       fields='sheets(data/rowData/values/userEnteredValue,properties(index,sheetId,title))').execute()
    sheet_index = 0
    sheet_name = result['sheets'][sheet_index]['properties']['title']
    last_row = len(result['sheets'][sheet_index]['data'][0]['rowData']) + 1
    size = [sheet_name, last_row]
    print("Sheet: " + spreadsheet + " | Size: " + str(last_row))
    return size


def save_to_sheet(sheet, range_name, values):
    body = {'values': [values], 'majorDimension': 'COLUMNS'}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption="USER_ENTERED",
                                   body=body).execute()
    print('{} cells updated.'.format(result.get('updatedCells')))


if __name__ == '__main__':
    main()
