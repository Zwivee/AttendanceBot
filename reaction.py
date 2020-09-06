import datetime
import discord
# import json
import os

# from discord.ext import commands
from dotenv import load_dotenv

# #instantiate an empty dict
# attendance = {}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
# #client = commands.Bot(command_prefix='!')
# with open("attendance.json") as f:
#     attendance = json.load(f)
# default_prefix = "!"

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
        # attendance[user.name] = currentDate


@client.event
async def on_reaction_remove(reaction, user):
    channel = reaction.message.channel
    await client.send_message(channel, '{} has removed {} from the message: {}'.format(user.name, reaction.emoji, reaction.message.content))

# @client.command(name='nw', help='Generates list of people who reacted to message with ✅ or \U0001fa91')
# async def nw(ctx):
#     with open('mydata.json', 'w') as f:
#         json.dump(attendance, f)

client.run(TOKEN)
