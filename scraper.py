from __future__ import print_function
import pickle
import os.path
import requests
import time
import json
import urllib.parse
import re
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
APPLICATION_NAME = "Google Sheets API Python"
TELEGRAM_BOT_ID = "TOKEN"
SPREADSHEET_ID = "SHEET ID"
RANGE_NAME = "RANGE"

def main():

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
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    #column = get_range(sheet)[0]
    size = len(values)
    start_row =2

    results=[]

    for i, row in enumerate(values):
        if row[0]=='Telegram':
            link = row[1]
            #url = get_telegram_url(link)
            actual_row = i+start_row
            #subscribers = get_telegram_subscribers(url)
            #save_to_sheet(sheet, column, actual_row, subscribers)
            results.append(str(actual_row)+": "+link)
        elif row[0]=='Instagram':
            url = row[1]
            actual_row = i+start_row
            #followers = get_instagram_followers(url)
            #save_to_sheet(sheet, column, actual_row, followers)
            results.append(str(actual_row)+": "+link)
        else:
            results.append("")
    save_to_sheet(sheet, "Media Channels!AP2:AP"+str(size+1), results)
    save_date(sheet, "Media Channels!AP1")

def get_telegram_subscribers(url):
    try:
        time.sleep(1000)
        response = requests.get(url)
  
        if response.status_code==200:
            response_json=json.loads(response.text)
            subscribers=response_json["result"]
            return subscribers
        elif response.status_code==400:
            return "NA"
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

def get_instagram_followers(url):
    try:
        time.sleep(1000)
        response = requests.get(url)

        if response.status_code==200:
            response_json = extract_shared_data_from_body(response.text)
            followers=response_json['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
            return followers
        elif response.status_code==400:
            return "NA"
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

def save_to_sheet(sheet, range_name, values):
    body = {'values': [values], 'majorDimension' : 'COLUMNS'}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption="USER_ENTERED", body=body).execute()
    print('{} cells updated.'.format(result.get('updatedCells')))

def save_date(sheet, range_name):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption="USER_ENTERED", body={"values":[[date]]}).execute()
    print('{} cells updated.'.format(result.get('updatedCells')))

def get_telegram_url(chat_url):
    chat_id="@"+chat_url[13:]
    url = "https://api.telegram.org/{}/getChatMembersCount?chat_id={}".format(TELEGRAM_BOT_ID, chat_id)
    return url

def get_range(sheet):
    last_row = sheet.getLastRow()
    last_column = sheet.getLastColumn()
  
    result = [last_column+1, last_row+1]
    return result

def extract_shared_data_from_body(body):
    """
    :param body: html string from a page
    :return: a dict extract from page
    """
    array = re.findall(r'_sharedData = .*?;</script>', body)
    if len(array) > 0:
        raw_json = array[0][len("_sharedData ="):-len(";</script>")]

        return json.loads(raw_json)

    return None

if __name__ == '__main__':
    main()
