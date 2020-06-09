
import requests
import time
import json
import urllib.parse
import re

FOLLOWERS_URL = 'https://www.instagram.com/graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables=%s'

def get_followers_json_link(variables):
    return FOLLOWERS_URL % urllib.parse.quote_plus(json.dumps(variables, separators=(',', ':')))

def get_followers(username):

    response = requests.get("https://www.instagram.com/{}/".format(username))

    if response.status_code != 200:
        print(response.status_code, ': Account with given username does not exist.')

    user_array = extract_shared_data_from_body(response.text)

    return user_array['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']

def get_account_id(username):

    response = requests.get("https://www.instagram.com/{}/".format(username))

    if  response.status_code == 400:
           print('Account with given username does not exist.')

    if response.status_code != 200:
            print(response.text, response.status_code)

    user_array = extract_shared_data_from_body(response.text)

    return user_array['entry_data']['ProfilePage'][0]['graphql']['user']['id']

def get_followers_by_id(account_id):
    #time.sleep()
    variables = {
        'id': str(account_id),
        'first': str(20),
        'after': ""
    }

    response = requests.get(get_followers_json_link(variables))
    #response = requests.get("https://www.instagram.com/imabdydayy/")

    if not response.status_code == 200:
        if response.status_code == 429:
            print("429 Too many requests")
            #time.sleep(random.uniform(rate_limit_sleep_min, rate_limit_sleep_max))

        #raise InstagramException.default(response.text, response.status_code)

    jsonResponse = response.json()

    followers = jsonResponse['data']['user']['edge_followed_by']['count']

    if followers == 0:
        print("NA")
    else:
        print(followers)

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

if __name__ == "__main__":
    print(get_followers("username"))
