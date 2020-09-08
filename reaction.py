import discord
import json
import os

from dotenv import load_dotenv
from json import JSONEncoder


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

position = 1

# Serialize data into json format
def write_json(data, filename='attendance.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@client.event
async def on_ready():
    print("Bot is logged in.")
    with open('attendance.json') as json_file:
        # Deserialize data from json to list
        data = json.load(json_file)

        temp = data['usr_details']
        # Clear data list of all data
        temp.clear()
        write_json(data)


@client.event
async def on_reaction_add(reaction, user):
    global position
    if reaction.emoji == '✅' or reaction.emoji == '\U0001fa91':
        with open('attendance.json') as json_file:
            data = json.load(json_file)

            temp = data['usr_details']

            # python object to appended
            if reaction.emoji == '✅':
                status = 'yes'
            elif reaction.emoji == '\U0001fa91':
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
    global position
    if reaction.emoji == '✅' or reaction.emoji == '\U0001fa91':
        to_keep = []

        with open('attendance.json', 'r') as json_file:
            data = json.load(json_file)
            temp = data['usr_details']
            for i in range(len(temp)):
                if temp[i]['name'] == user.name:
                    del temp[i]

            write_json(data)
            position -= 1

client.run(TOKEN)
