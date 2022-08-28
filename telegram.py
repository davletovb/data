"""
Donwload messages from telegram channel and save it to a csv file.
"""

import configparser
import json
import asyncio
from datetime import date, datetime

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')

# Telegram API
api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
api_hash = str(api_hash)
phone = config['telegram']['phone']
username = config['telegram']['username']

# Parse json date
class JSONDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, bytes):
            return list(obj)
        
        return json.JSONEncoder.default(self, obj)


# Telegram client
client = TelegramClient(username, api_id, api_hash)

# Connect to telegram
async def main(phone):
    await client.start()
    print('Connected to Telegram')
    # Check if authorized
    if not (await client.is_user_authorized()):
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Enter your password: '))
        
        print('Authorized')

        me = await client.get_me()

        # Get channel id from input
        channel_id = input('Enter channel id or URL: ')

        # If channel id is not URL, get channel id from URL
        if channel_id.isdigit():
            channel_url = PeerChannel(int(channel_id))
        else:
            channel_url = channel_id
        
        entity = await client.get_entity(channel_url)

        # Get messages from channel
        offset = 0
        limit = 100
        total_messages = 0
        total_count_limit = 0
        messages = []

        while True:
            print("Current offset: {}; Total messages: {}".format(offset, total_messages))
            history = await client(GetHistoryRequest(
                entity,
                offset=offset,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
            messages_history = history.messages
            for message in messages_history:
                messages.append(message.to_dict())
            total_messages += len(history.messages)
            offset = history.messages[-1].id
            if total_count_limit > total_messages:
                break

        # Save messages to csv file
        with open('messages.csv', 'w') as f:
            for message in messages:
                f.write(json.dumps(message, cls=JSONDateTimeEncoder) + '\n')
        print('Done')

with client:
    client.loop.run_until_complete(main(phone))



