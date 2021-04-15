import discord
import os
import re
import datetime
import gspread
import asyncio

from dotenv import load_dotenv
from discord.ext import commands, tasks
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
        nwWeekDay = datetime.datetime.strptime(match.group(),
                                               '%m/%d/%y').date().weekday()
        return nwWeekDay


def updateCell(inGameName, nwWeekDay, status):
    try:
        cell = worksheet.find(inGameName)
    except:
        print("Cannot find name")
    else:
        # Since we do not node war on Saturday the sheet is missing a column and therefor sunday must be calculated with an offset
        if nwWeekDay != 6:
            worksheet.update_cell(cell.row, nwWeekDay + 11, status)
        else:
            worksheet.update_cell(cell.row, nwWeekDay + 10, status)


def checkTodaysAttendanceInSheets(nwWeekDay):
    if nwWeekDay != 6:
        currentAttendance = worksheet.cell(2, nwWeekDay + 11).value
    else:
        currentAttendance = worksheet.cell(2, nwWeekDay + 10).value
    return int(currentAttendance)

@bot.event
async def on_reaction_add(reaction, user):
    inGameName = getUser(user)
    nwWeekDay = calculateWeekdayFromAnnouncement(reaction)
    if nwWeekDay is not None:
        if (reaction.emoji == '✅') and (
                checkTodaysAttendanceInSheets(nwWeekDay) < int(nodeCapacity)):
            updateCell(inGameName, nwWeekDay, 'TRUE')


@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji == '✅':
        inGameName = getUser(user)
        nwWeekDay = calculateWeekdayFromAnnouncement(reaction)
        if nwWeekDay is not None:
            updateCell(inGameName, nwWeekDay, 'FALSE')


@bot.command(pass_context=True, alias=["quit"])
@commands.has_permissions(administrator=True)
async def kill(ctx):
    # Allow any server administrators to kill the bottom
    await bot.close()
    print('Bot is logged out')


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def cap(ctx, capacitySetting):
    global nodeCapacity
    nodeCapacity = capacitySetting

    # Reply with message and new capacity set
    await ctx.channel.send('Node Cap: {}'.format(nodeCapacity))


def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (
            future_exec - now
    ).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(
            now + datetime.timedelta(days=1), given_time)  # days always >= 0

    return (future_exec - now).total_seconds()


@tasks.loop(hours=24)
async def resetCap():
    await asyncio.sleep(seconds_until(18, 00))
    global nodeCapacity
    nodeCapacity = 100
    print('Node Capacity Reset')


resetCap.start()

# Run bot
bot.run(TOKEN)
