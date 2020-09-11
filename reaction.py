import discord
import json
import os

from dotenv import load_dotenv
from json import JSONEncoder

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

# Serialize data into json format
def write_json(data, filename='attendance.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@client.event
async def on_ready():
    print("Bot is logged in.")
    with open('attendance.json', 'r') as json_file:
        # Deserialize data from json to lists
        data = json.load(json_file)
        yesList = data['✅']
        chairList= data['🪑']

        # Clear data list of all data
        yesList.clear()
        chairList.clear()

        write_json(data)

@client.event
async def on_reaction_add(reaction, user):
    newPerson=user.name
    with open('attendance.json', 'r') as json_file:
        data = json.load(json_file)
        yesList=data['✅']
        chairList=data['🪑']

        if reaction.emoji == '✅':
            #Append to yesList
            yesList.append(newPerson)
        elif reaction.emoji == '🪑':
            chairList.append(newPerson)
        with open('attendance.json', 'w') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

@client.event
async def on_reaction_remove(reaction, user):

    if reaction.emoji == '✅' or reaction.emoji == '\U0001fa91':
        to_keep = []

        with open('attendance.json', 'r') as json_file:
            data = json.load(json_file)
            temp = data['attendance']
            for i in range(len(temp)):
                if temp[i]['name'] == user.name:
                    print(i)
                    temp.pop(i)
                    print("Got here")

            with open('attendance.json', 'w') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

client.run(TOKEN)
