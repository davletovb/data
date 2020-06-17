from __future__ import print_function
import pickle
import os.path
import requests
import random
import json
import urllib.parse
import re
import datetime
from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from pypac import PACSession, get_pac
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
APPLICATION_NAME = "Google Sheets API Python"
TELEGRAM_BOT_ID = [
    "BOT ID"]
SPREADSHEET_ID = "SHEET ID"
YOUTUBE_API_KEY = "API KEY"
PROXIES = [
    'ADDRESS']
PROXY = "PAC FILE URL"
PAC = get_pac(url=PROXY)
GECKO_PATH = "GECKO PATH"
INSTAGRAM_ACCOUNT = {
  0 : {
    "username" : "username",
    "password" : "password"
  }}

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
    
    # Initialize browser and set up proxy
    selenium_proxy = webdriver.Proxy()
    selenium_proxy.proxy_type = webdriver.common.proxy.ProxyType.PAC
    selenium_proxy.proxyAutoconfigUrl = PROXY

    profile = webdriver.FirefoxProfile()
    profile.set_proxy(selenium_proxy)

    driver = webdriver.Firefox(executable_path=GECKO_PATH)
    # Login Instagram account
    instagram_login(driver)

    # Call the Sheets API
    sheet = service.spreadsheets()
    sheet_name, column, size = get_range(sheet)
    start_row = 2
    end_row = size
    working_range = sheet_name+"!C"+str(start_row)+":D"+str(end_row)
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=working_range).execute()
    values = result.get('values', [])

    results=[]

    for i, row in enumerate(values):
        print(datetime.datetime.now().strftime("%H:%M:%S")+" - "+str(i)+" - "+row[1])
        if row[0]=='Telegram':
            url = row[1]
            #link = get_telegram_url(url)
            subscribers = get_telegram_subscribers(url, driver)
            print(subscribers)
            results.append(subscribers)
        elif row[0]=='Instagram':
            url = row[1]
            followers = get_instagram_followers(url, driver)
            print(followers)
            results.append(followers)
        elif row[0]=='YouTube':
            url = row[1]
            channel_id = get_youtube_url(url)
            subscribers = get_youtube_subscribers(channel_id)
            print(subscribers)
            results.append(subscribers)
        elif row[0]=='Twitter':
            url = row[1]
            followers = get_twitter_followers(url, driver)
            print(followers)
            results.append(followers)
        elif row[0]=='VK':
            url = row[1]
            followers = get_vk_followers(url, driver)
            print(followers)
            results.append(followers)
        elif row[0]=='OK':
            url = row[1]
            followers = get_ok_followers(url, driver)
            print(followers)
            results.append(followers)
        else:
            results.append("")
    
    save_to_sheet(sheet, sheet_name+"!"+column+str(start_row)+":"+column+str(end_row), results)
    save_date(sheet, sheet_name+"!"+column+str(1))
    driver.quit()

def get_telegram_subscribers(url, driver):
    try:
        sleep(random.uniform(3.0,7.0))
        #session = PACSession(PAC)
        driver.get(url)
        soup = bs(driver.page_source,"lxml")
        #response = requests.get(url, proxies = {'http' : PROXIES[random.randint(0,4)]})
        #response = session.get(url)
        #soup = bs(response.text, 'html.parser')
        result = soup.findAll('div', {'class':'tgme_page_extra'})
        if result:
            subscribers = re.split(r'\s\D',result[0].text.strip())[0].replace(" ","")
            if subscribers.isdigit():
                return subscribers
            else:
                return "NA"
        elif not result:
            return "NA"
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

def get_instagram_followers(url, driver):
    try:
        sleep(random.uniform(3.0,7.0))
        driver.get(url)
        soup = bs(driver.page_source,"lxml")
        result = soup.findAll("span",{"class":"g47SY"})
        if result:
            followers = result[1]["title"].replace(",","")
            return followers
        else:
            return "NA"
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

def instagram_login(driver):
    account = INSTAGRAM_ACCOUNT[random.randint(0,2)]
    driver.get('https://www.instagram.com/accounts/login/')
    print("Logging in: "+account["username"])
    sleep(3)
    driver.find_element_by_name("username").send_keys(account["username"])
    sleep(1)
    driver.find_element_by_name("password").send_keys(account["password"])
    sleep(1)
    driver.find_element_by_tag_name('form').submit()
    sleep(3)

def get_youtube_subscribers(url):
    try:
        sleep(2)
        response = requests.get(url)
        response_json = response.json()
        if "items" in response_json:
            subscribers = response_json["items"][0]["statistics"]["subscriberCount"]
            return subscribers
        else:
            return "NA"
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

def get_twitter_followers(url, driver):
    try:
        sleep(random.uniform(3.0,7.0))
        driver.get(url)
        soup = bs(driver.page_source,"lxml")
        result = soup.select('div > a')
        if result:
            followers = result[5]["title"].replace(",","")
            return followers
        else:
            return "NA"
    except:
        return "NA"

def get_vk_followers(url, driver):
    try:
        sleep(3)
        driver.get(url)
        soup = bs(driver.page_source,"lxml")
        result = soup.findAll("div",{"class":"count"})
        if result:
            followers = result[0].text.replace(",","")
            return followers
        else:
            result = soup.find("div",{"id":["public_followers","group_followers"]})
            if result is not None:
                followers = result.find("span",{"class":"header_count"}).text.replace(",","")
                return followers
            else:
                return "NA"
    except:
        return "NA"

def get_ok_followers(url, driver):
    try:
        sleep(3)
        driver.get(url)
        soup = bs(driver.page_source,"lxml")
        result = soup.find("span",{"class":"portlet_h_count"})
        if result:
            followers = int(''.join(filter(str.isdigit, result.text)))
            return followers
        else:
            result = soup.find("span",{"class":"navMenuCount"})
            if result is not None:
                followers = ''.join(filter(str.isdigit, result.text))
                return followers
            else:
                return "NA"
    except:
        return "NA"
        
def save_to_sheet(sheet, range_name, values):
    body = {'values': [values], 'majorDimension' : 'COLUMNS'}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption="USER_ENTERED", body=body).execute()
    print('{} cells updated.'.format(result.get('updatedCells')))

def save_date(sheet, range_name):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption="USER_ENTERED", body={"values":[[date]]}).execute()
    print('{} cells updated.'.format(result.get('updatedCells')))

def get_telegram_url(chat_url):
    chat_id = "@"+chat_url[13:]
    bot_id = TELEGRAM_BOT_ID[random.randint(0,3)]
    url = "https://api.telegram.org/{}/getChatMembersCount?chat_id={}".format(bot_id, chat_id)
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

if __name__ == '__main__':
    main()
