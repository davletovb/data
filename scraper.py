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
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
APPLICATION_NAME = "Google Sheets API Python"
TELEGRAM_BOT_ID="TOKEN"
SPREADSHEET_ID = "ID"
RANGE_NAME = "RANGE"
YOUTUBE_API_KEY="API KEY"

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
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    sheet_name, column, size = get_range(sheet)
    start_row =2

    results=[]

    for i, row in enumerate(values):
        print(str(i)+": "+row[1])
        if row[0]=='Telegram':
            link = row[1]
            url = get_telegram_url(link)
            subscribers = get_telegram_subscribers(url)
            results.append(subscribers)
        elif row[0]=='Instagram':
            url = row[1]
            followers = get_instagram_followers(url)
            results.append(followers)
        elif row[0]=='YouTube':
            url = row[1]
            channel_id = get_telegram_url(url)
            subscribers = get_youtube_subscribers(channel_id)
            results.append(subscribers)
        else:
            results.append("")

    save_to_sheet(sheet, sheet_name+"!"+column+str(start_row)+":"+column+str(size), results)
    save_date(sheet, sheet_name+"!"+column+str(1))

def get_telegram_subscribers(url):
    try:
        time.sleep(5)
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
        time.sleep(3)
        response = requests.get(url)
        if response.status_code==200:
            try:
                response_json = extract_shared_data_from_body(response.text)
                followers=response_json['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
                return followers
            except:
                return "NA"
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

def get_youtube_subscribers(url):
    try:
        time.sleep(3)
        response = requests.get(url)
        if response.status_code==200:
            try:
                response_json = response.json()
                subscribers = response_json["items"][0]["statistics"]["subscriberCount"]
                return subscribers
            except:
                return "NA"
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

def get_youtube_url(channel_url):
    channel_id=channel_url[32:]
    url="https://www.googleapis.com/youtube/v3/channels?part=statistics&id={}&key={}".format(channel_id, YOUTUBE_API_KEY)
    return url

def get_range(sheet):
    result = sheet.get(spreadsheetId=SPREADSHEET_ID, fields='sheets(data/rowData/values/userEnteredValue,properties(index,sheetId,title))').execute()
    sheet_index = 0
    sheet_name = result['sheets'][sheet_index]['properties']['title']
    last_row = len(result['sheets'][sheet_index]['data'][0]['rowData'])+1
    last_column_number = max([len(e['values']) for e in result['sheets'][sheet_index]['data'][0]['rowData'] if e])
    X = lambda n:~int(n) and X(int(n/26)-1)+chr(65+n%26)or''
    last_column = X(last_column_number)
    size = [sheet_name, last_column, last_row]
    return size

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
