import datetime
import discord
import json
import os

from dotenv import load_dotenv
from json import JSONEncoder


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


def write_json(data, filename='attendance.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


# # subclass JSONEncoder
# class DateTimeEncoder(JSONEncoder):
#     # Override the default method
#     def default(self, obj):
#         if isinstance(obj, (datetime.date, datetime.datetime)):
#             return obj.isoformat()


@client.event
async def on_ready():
    print("Bot is logged in.")


@client.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    currentDate = datetime.datetime.now()
    await client.send_message(channel, '{} has added {} to the message: {}'.format(user.name, reaction.emoji, reaction.message.content))
    if reaction.emoji == '✅' or reaction.emoji == '\U0001fa91':
        await client.send_message(channel, currentDate)
        with open('attendance.json') as json_file:
            data = json.load(json_file)

            temp = data['usr_details']

            # python object to appended
            y = {user.name: reaction.emoji

                 }

            # appending data to emp_details
            temp.append(y)

            write_json(data)


@client.event
async def on_reaction_remove(reaction, user):
    channel = reaction.message.channel
    await client.send_message(channel, '{} has removed {} from the message: {}'.format(user.name, reaction.emoji, reaction.message.content))

client.run(TOKEN)
