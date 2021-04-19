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
maxAttendace = 100
global nodeCapacity
nodeCapacity = maxAttendace
colContainingNames = 2
monToFriOffset = 11
sundayOffset = 10
sunday = 6
nodeCapacityResetTimer = 24  # in hours
hourOfDayToeset = 18  # military time
minuteOfHourToReset = 00


# Bot started
@bot.event
async def on_ready():
    print("Bot is logged in.")


# Name of user that added reacted to message
def getUser(user):
    newPerson = user.display_name
    inGameNameQ = newPerson.split(' ', 1)[0]
    inGameName = inGameNameQ.replace('"', '')
    return inGameName


# Find message date and give weekday in for of 0 Monday - 6 Sunday
def calculateWeekdayFromAnnouncement(reaction):
    message = reaction.message.content

    match = re.search('\d{1}/\d{2}/\d{2}', message)
    if match is not None:
        nwWeekDay = datetime.datetime.strptime(match.group(),
                                               '%m/%d/%y').date().weekday()
        return nwWeekDay


# Find the cell in google sheet that matches inGameName and try to update the correct day
def updateCell(inGameName, nwWeekDay, status):
    try:
        # \b binds results to whole words, and used built in ignore case method
        caseInsensitiveCheck = re.compile(rf"\b{inGameName}\b", re.IGNORECASE)
        cell = worksheet.find(caseInsensitiveCheck)
    except:
        print("Cannot find name" + inGameName)
    else:
        # Since we do not node war on Saturday the sheet is missing a column and therefor sunday must be calculated with an offset
        if nwWeekDay != sunday:
            worksheet.update_cell(cell.row, nwWeekDay + monToFriOffset, status)
        else:
            worksheet.update_cell(cell.row, nwWeekDay + sundayOffset, status)


# Since we do not node war on Saturday the sheet is missing a column and therefore sunday must be calculated with an offset.
def checkTodaysAttendanceInSheets(nwWeekDay):
    if nwWeekDay != sunday:
        currentAttendance = worksheet.cell(colContainingNames,
                                           nwWeekDay + monToFriOffset).value
    else:
        currentAttendance = worksheet.cell(colContainingNames,
                                           nwWeekDay + sundayOffset).value
    return int(currentAttendace)

  
# Triggers when message in channel has ✅ added from message. Reads the date and updates the correct cell in google sheets.
@bot.event
async def on_reaction_add(reaction, user):
    inGameName = getUser(user)
    nwWeekDay = calculateWeekdayFromAnnouncement(reaction)
    if nwWeekDay is not None:
        if (reaction.emoji == '✅') and (
                checkTodaysAttendanceInSheets(nwWeekDay) < int(nodeCapacity)):
            updateCell(inGameName, nwWeekDay, 'TRUE')


# Triggers when message in channel has ✅ removed from message. Reads the date and updates the correct cell in google sheets.
@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji == '✅':
        inGameName = getUser(user)
        nwWeekDay = calculateWeekdayFromAnnouncement(reaction)
        if nwWeekDay is not None:
            updateCell(inGameName, nwWeekDay, 'FALSE')


# Handler for command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing a required argument. Do !help")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You do not have the appropriate permissions to run this command.")
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have sufficient permissions!")
    else:
        print("Error not caught")
        print(error)


# Command !kill that can only be used by server administrators to stop the bot
@bot.command(pass_context=True, alias=["quit"])
@commands.has_permissions(administrator=True)
async def Kill(ctx):
    # Allow any server administrators to kill the bottom
    await bot.close()
    print('Bot is logged out')


# Command !cap that can only be used by server administrators to change the node war cap
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def Cap(ctx, capacitySetting):
    global nodeCapacity
    nodeCapacity = capacitySetting

    # Reply with message and new capacity set
    await ctx.channel.send('Node Cap: {}'.format(nodeCapacity))


# Starts a command group for the help command
# Command groups will expand on a certain command such as help <command>
@bot.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(
        title="Help",
        description=
        "Use !help <command> for extended information on a command.",
        color=ctx.author.color)
    em.add_field(name="Moderation", value="Kill")
    em.add_field(name="Basic", value="Cap")

    await ctx.send(embed=em)


# Part of help command group expand on the help command
# Will not return base help command, but will instead return declared embed
@help.command()
async def kill(ctx):
    em = discord.Embed(title="Kill",
                       description="Kill the bot",
                       color=ctx.author.color)

    await ctx.send(embed=em)


# Part of help command group expand on the help command
# Will not return base help command, but will instead return declared embed
@help.command()
async def cap(ctx):
    em = discord.Embed(title="Cap",
                       description="Changes attendace capacity.",
                       color=ctx.author.color)
    em.add_field(name="**Syntax**", value="!cap <number>")

    await ctx.send(embed=em)


# Timer to calculate when to run the task to reset nodewar cap automatically
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


# Resets the node war cap variable every day, current setting at 6pm pst v2.1.2
@tasks.loop(hours=nodeCapacityResetTimer)
async def resetCap():
    await asyncio.sleep(seconds_until(hourOfDayToeset, minuteOfHourToReset))
    global nodeCapacity
    nodeCapacity = maxAttendace
    print('Node Capacity Reset')


resetCap.start()

# Run bot
bot.run(TOKEN)
