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
SHEET = os.getenv('SHEET_ID')
prefix = '!'

# Initialization discord
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command('help')

# Initialize gspread
gc = gspread.service_account(filename='keys.json')
sh = gc.open_by_key(SHEET)
worksheet = sh.worksheet('Master List')

# Global settings
# Currently if we want to restrain the number of people that can be checked, but this will become obsolete when uncapped begins
global nodeCapacity
nodeCapacity = 100

# Bot started


@bot.event
async def on_ready():
    print("Bot is logged in.")

def getUser(user):
    # Name of user that added reacted to message
    newPerson = user.display_name
    inGameNameQ = newPerson.split(' ', 1)[0]
    inGameName = inGameNameQ.replace('"', '')
    return inGameName


def calculateWeekdayFromAnnouncement(reaction):
    # Find message date and give weekday in for of 0 Monday - 6 Sunday
    message = reaction.message.content

    match = re.search('\d{1}/\d{2}/\d{2}', message)
    if match is not None:
        nwWeekDay = datetime.datetime.strptime(
            match.group(), '%m/%d/%y').date().weekday()
        return nwWeekDay


def updateCell(inGameName, nwWeekDay, status):
    cell = worksheet.find(inGameName)
    worksheet.update_cell(cell.row, nwWeekDay+11, status)


def checkTodaysAttendanceInSheets(nwWeekDay):
    currentAttendance = worksheet.cell(2,nwWeekDay+11).value
    return int(currentAttendance)

@bot.event
async def on_reaction_add(reaction, user):
    inGameName = getUser(user)
    nwWeekDay = calculateWeekdayFromAnnouncement(reaction)
    if nwWeekDay is not None:
        if (reaction.emoji == '✅') and (checkTodaysAttendanceInSheets(nwWeekDay) < int(nodeCapacity)):
            updateCell(inGameName, nwWeekDay, 'TRUE')



@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji == '✅':
        inGameName = getUser(user)
        nwWeekDay = calculateWeekdayFromAnnouncement(reaction)
        if nwWeekDay is not None:
            updateCell(inGameName, nwWeekDay, 'FALSE')



@bot.command(pass_context=True)
async def kill(ctx):
    # Allow any server administrators to kill the bottom
    if ctx.message.author.server_permissions.administrator:
        await bot.logout()


@bot.command(pass_context=True)
async def cap(ctx, capacitySetting):
    if ctx.message.author.server_permissions.administrator:
        global nodeCapacity
        nodeCapacity = capacitySetting

        # Reply with message and new capacity set
        await ctx.channel.send('Node Cap: {}'.format(nodeCapacity))

# Run bot
bot.run(TOKEN)
