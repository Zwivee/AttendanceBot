import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print("Bot is logged in.")

@client.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    await client.send_message(channel, '{} has added {} to the message: {}'.format(user.name,reaction.emoji,reaction.message.content))

@client.event
async def on_reaction_remove(reaction, user):
    channel = reaction.message.channel
    await client.send_message(channel, '{} has removed {} from the message: {}'.format(user.name,reaction.emoji,reaction.message.content))

client.run(TOKEN)
