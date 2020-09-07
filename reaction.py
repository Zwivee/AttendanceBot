import datetime
import discord
import json
import os

from dotenv import load_dotenv
from json import JSONEncoder


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

position = 1
def write_json(data, filename='attendance.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

@client.event
async def on_ready():
    print("Bot is logged in.")


@client.event
async def on_reaction_add(reaction, user):
    global position
    channel = reaction.message.channel
    currentDate = datetime.datetime.now()
    await client.send_message(channel, '{} has added {} to the message: {}'.format(user.name, reaction.emoji, reaction.message.content))
    if reaction.emoji == '✅' or reaction.emoji == '\U0001fa91':
        await client.send_message(channel, currentDate)
        with open('attendance.json') as json_file:
            data = json.load(json_file)

            temp = data['usr_details']

            # python object to appended
            if reaction.emoji == '✅':
                status = 'yes'
            elif reaction.emoji =='\U0001fa91':
                status = 'chair'
            y = {"name": user.name,
                "status": status,
                "position": position
                 }

            # appending data to emp_details
            temp.append(y)

            write_json(data)
            position += 1

@client.event
async def on_reaction_remove(reaction, user):
    channel = reaction.message.channel
    await client.send_message(channel, '{} has removed {} from the message: {}'.format(user.name, reaction.emoji, reaction.message.content))
    if reaction.emoji == '✅' or reaction.emoji == '\U0001fa91':
        with open('attendance.json') as json_file:
            data = json.load(json_file)
        for element in data:
           del element["user.name"]

    write_json(data)
client.run(TOKEN)
