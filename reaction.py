import discord
import os
import pandas as pd

from dotenv import load_dotenv
from discord.ext import commands
from datetime import date

# Load environment settings for discord token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
prefix='!'

# Initialization discord
bot = commands.Bot(command_prefix = prefix)
bot.remove_command('help')

# Initialize empty lists
yesList = []
chairList= []

# bot started
@bot.event
async def on_ready():
    print("Bot is logged in.")
    yesList.clear()
    chairList.clear ()

@bot.event
async def on_reaction_add(reaction, user):
    # Name of user that added reacted to message
    newPerson=user.name

    if reaction.emoji == '✅':
        # Append to yesList
        yesList.append(newPerson)
    elif reaction.emoji == '🪑':
        # Append to chairList
        chairList.append(newPerson)

@bot.event
async def on_reaction_remove(reaction, user):
    # Name of user that removed reaction
    newPerson=user.name

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

@bot.command(pass_context=True)
async def attendance(ctx):

    df = pd.DataFrame()

    # Create two columns
    # Workaround for imbalanced lists in Pandas. Make lists into series first
    # before export to fill all empty elements in list with NaN.
    df['✅'] = pd.Series(yesList,dtype='float64')
    df['🪑'] = pd.Series(chairList,dtype='float64')

    # Convert to excel
    df.to_excel('attendance.xls', index = False)

    # Get current date
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")

    # Reply with message and current date.
    await ctx.send('Attendance excel generated on {}'.format(d1))
    # await bot.send_message(ctx.message.channel,'Attendance excel generated on {}'.format(d1))

    # Clear lists
    yesList.clear()
    chairList.clear()

# Run bot
bot.run(TOKEN)
