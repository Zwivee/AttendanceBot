import discord
import os
import re
import datetime
import gspread

from dotenv import load_dotenv
from discord.ext import commands
from datetime import date


# Load environment settings for discord token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
prefix = '!'

# Initialization discord
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command('help')

# Initialize gspread
gc = gspread.service_account(filename='keys.json')

sh = gc.open_by_key('SHEET_ID')
worksheet = sh.worksheet('Master List')

# Bot started
@bot.event
async def on_ready():
    print("Bot is logged in.")


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '✅':
        # Name of user that added reacted to message
        newPerson = user.display_name
        inGameNameQ = newPerson.split(' ', 1)[0]
        inGameName = inGameNameQ.replace('"', '')
        message = reaction.message.content

        # Find message date and give weekday in for of 0 Monday - 6 Sunday
        match = re.search('\d{1}/\d{2}/\d{2}', message)
        nwWeekDay = datetime.datetime.strptime(
            match.group(), '%m/%d/%y').date().weekday()

        cell = worksheet.find(inGameName)
        worksheet.update_cell(cell.row,nwWeekDay+11,'TRUE')



@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji == '✅':
        # Name of user that added reacted to message
        newPerson = user.display_name
        inGameNameQ = newPerson.split(' ', 1)[0]
        inGameName = inGameNameQ.replace('"', '')
        message = reaction.message.content

        # Find message date and give weekday in for of 0 Monday - 6 Sunday
        match = re.search('\d{1}/\d{2}/\d{2}', message)
        nwWeekDay = datetime.datetime.strptime(
            match.group(), '%m/%d/%y').date().weekday()

        cell = worksheet.find(inGameName)
        worksheet.update_cell(cell.row,nwWeekDay+11,'FALSE')


@bot.command(pass_context=True)
async def attendance(ctx):

    # Get current date
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")

    # Reply with message and current date.
    await ctx.send('Attendance excel generated on {}'.format(d1))

# Run bot
bot.run(TOKEN)
