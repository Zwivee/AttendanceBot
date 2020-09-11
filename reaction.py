import discord
import json
import os
import pandas as pd

from dotenv import load_dotenv
from discord.ext import commands
from json import JSONEncoder

# Load environment settings for discord token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
prefix='!'

# Initialization
client = discord.Client()
client = commands.Bot(command_prefix = prefix)
client.remove_command('help')

# Serialize data into json format
def write_json(data, filename='attendance.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Remove all data from json file
def clear_json():
    with open('attendance.json', 'r') as json_file:
        # Deserialize data from json to lists
        data = json.load(json_file)
        yesList = data['✅']
        chairList= data['🪑']

        # Clear data list of all data
        yesList.clear()
        chairList.clear()

        write_json(data)
# Bot started
@client.event
async def on_ready():
    print("Bot is logged in.")
    clear_json()

@client.event
async def on_reaction_add(reaction, user):
    # Name of user that added reacted to message
    newPerson=user.name
    # Open json in read mode
    with open('attendance.json', 'r') as json_file:
        # Deserialize json file
        data = json.load(json_file)
        # Get pointer to lists
        yesList=data['✅']
        chairList=data['🪑']

    if reaction.emoji == '✅':
        # Append to yesList
        yesList.append(newPerson)
    elif reaction.emoji == '🪑':
        # Append to chairList
        chairList.append(newPerson)

    with open('attendance.json', 'w') as json_file:
        # Serialize json data and format it. Allow for ascii character to show
        json.dump(data, json_file, ensure_ascii=False, indent=4)

@client.event
async def on_reaction_remove(reaction, user):
    # Name of user that removed reaction
    newPerson=user.name
    # Open json in read mode
    with open('attendance.json', 'r') as json_file:
        # Deserialize json file
        data = json.load(json_file)
        # Get pointer to lists
        yesList=data['✅']
        chairList=data['🪑']

    if reaction.emoji == '✅':
        # Search the length of list
        for i in range(len(yesList)):
            # Name matching person that removed reaction found
            if yesList[i] == user.name:
                # Remove user
                yesList.pop(i)
    elif reaction.emoji == '🪑':
        for i in range(len(chairList)):
            if chairList[i] == user.name:
                chairList.pop(i)

    with open('attendance.json', 'w') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

@client.command()
async def attendance():
    # Pandas to translate from json to xls
    df_json = pd.read_json('attendance.json')
    df_json.to_excel('attendance.xls')

    # Clear the json again to start new tally
    clear_json()
# Run bot
client.run(TOKEN)
