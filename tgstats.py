import requests
import json
from time import sleep

# The ID, TOKEN and API KEY
APPLICATION_NAME = "Scrape Stats"
TELEGRAM_BOT_ID="TOKEN"
SPREADSHEET_ID = "ID"
YOUTUBE_API_KEY="API KEY"

def main():

    sheet_name, column, size = google_sheet.get_range(SPREADSHEET_ID)
    start_row = 2
    end_row = size
    results=[]
    values = google_sheet.get_values(SPREADSHEET_ID)
    
    # Filter Telegram links from list of channels and get subscribers
    for i, row in enumerate(values):
        print(str(i)+": "+row[1])
        if row[0]=='Telegram':
            link = row[1]
            url = get_telegram_url(link)
            subscribers = get_telegram_subscribers(url)
            print(subscribers)
            results.append(subscribers)
        else:
            results.append("")

    google_sheet.save_to_sheet(SPREADSHEET_ID, sheet_name+"!"+column+str(start_row)+":"+column+str(size), results)

# Get Telegram subscriber for a specific channel
def get_telegram_subscribers(url):
    try:
        sleep(5)
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

# Get Telegram API url for a specific channel
def get_telegram_url(chat_url):
    chat_id="@"+chat_url[13:]
    url = "https://api.telegram.org/{}/getChatMembersCount?chat_id={}".format(TELEGRAM_BOT_ID, chat_id)
    return url

if __name__ == '__main__':
    main()
