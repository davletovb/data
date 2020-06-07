import requests
import json

bot_id="TOKEN"
chat_url="https://t.me/channelname"
chat_id="@"+chat_url[13:]

response = requests.get("https://api.telegram.org/{}/getChatMembersCount?chat_id={}".format(bot_id, chat_id))

if response.status_code==requests.codes.ok:
    response_json=json.loads(response.text)
    subscribers=response_json["result"]
    print(subscribers)
else:
    print("NA")
