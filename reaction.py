import os
import re
import datetime
import asyncio
import discord
import gspread

from dotenv import load_dotenv
from discord.ext import commands, tasks

# Load environment settings for discord token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SHEET = os.getenv('SHEET_ID')
PREFIX = '!'

# Initialization discord
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.remove_command('help')

# Initialize gspread
gc = gspread.service_account(filename='keys.json')
sh = gc.open_by_key(SHEET)
worksheet = sh.worksheet('Master List')

# Global settings
# Currently if we want to restrain the number of people
# that can be checked, but this will become obsolete when uncapped begins
MAX_ATTENDANCE = 100
global NODE_CAPACITY
NODE_CAPACITY = MAX_ATTENDANCE
COL_CONTAIN_IN_GAMES = 2
MON_TO_FRI_OFFSET = 11
SUNDAY_OFFSET = 10
SUNDAY = 6
NODE_CAPACITY_RESET_TIMER = 24  # in hours
HOUR_OF_DAY_TO_RESET = 18  # military time
MINUTE_OF_HOUR_TO_RESET = 00
extra_list = []
current_nw_weekday = None


# Bot started
@bot.event
async def on_ready():
    print("Bot is logged in.")


# Name of user that added reacted to message
def get_user(user):
    new_person = user.display_name
    pattern = '''"([^"]*)"'''
    in_game_name = re.findall(pattern, new_person, re.IGNORECASE)
    if in_game_name:
        result = in_game_name[0]
    else:
        print("Could not find the user from the string " + new_person)
    return result


# Find message date and give weekday in for of 0 Monday - 6 Sunday
def calculate_weekday_from_announcement(reaction):
    message = reaction.message.content
    match = re.search(r'\d{1}/\d{2}/\d{2}', message)
    if match is not None:
        nw_weekday = datetime.datetime.strptime(match.group(),
                                                '%m/%d/%y').date().weekday()
        return nw_weekday


# Find the cell in google sheet that matches
# inGameName and try to update the correct day
def update_cell(in_game_name_update, target_weekday, status):
    try:
        # \b binds results to whole words, and used built in ignore case method
        whole_word_match_ign = re.compile(rf"\b{in_game_name_update}\b")
        cell = worksheet.find(whole_word_match_ign)
    except gspread.CellNotFound:
        print("Cannot find name " + in_game_name_update)
    else:
        # Since we do not node war on Saturday the sheet is missing a column
        # and therefore sunday must be calculated with an offset
        if target_weekday != SUNDAY:
            worksheet.update_cell(cell.row, target_weekday + MON_TO_FRI_OFFSET,
                                  status)
        else:
            worksheet.update_cell(cell.row, target_weekday + SUNDAY_OFFSET,
                                  status)


# Since we do not node war on Saturday the sheet is missing a column
# and therefore sunday must be calculated with an offset.
def check_todays_attendance_in_sheets(target_nw_weekday_to_check):
    if target_nw_weekday_to_check != SUNDAY:
        current_attendance = worksheet.cell(
            COL_CONTAIN_IN_GAMES,
            target_nw_weekday_to_check + MON_TO_FRI_OFFSET).value
    else:
        current_attendance = worksheet.cell(
            COL_CONTAIN_IN_GAMES,
            target_nw_weekday_to_check + SUNDAY_OFFSET).value
    return int(current_attendance)


# Triggers when message in channel has ✅ added from message
# Reads the date and updates the correct cell in google sheets.
@bot.event
async def on_reaction_add(reaction, user):
    user_in_game_name = get_user(user)
    global current_nw_weekday
    current_nw_weekday = calculate_weekday_from_announcement(reaction)
    # Check if officer posting did not place date in announcement
    if current_nw_weekday is not None:
        if (reaction.emoji == '✅') and (
                check_todays_attendance_in_sheets(current_nw_weekday) <
                int(NODE_CAPACITY)):
            update_cell(user_in_game_name, current_nw_weekday, 'TRUE')
        elif ((check_todays_attendance_in_sheets(current_nw_weekday) >=
               int(NODE_CAPACITY))):
            extra_list.append(user_in_game_name)


# Triggers when message in channel has ✅ removed from message
# Reads the date and updates the correct cell in google sheets.
@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji == '✅':
        user_in_game_name = get_user(user)
        current_nw_weekday = calculate_weekday_from_announcement(reaction)
        # Check if officer posting did not place date in announcement
        if current_nw_weekday is not None:
            update_cell(user_in_game_name, current_nw_weekday, 'FALSE')
        elif ((check_todays_attendance_in_sheets(current_nw_weekday) >=
               int(NODE_CAPACITY))):
            extra_list.pop(user_in_game_name)


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
async def kill():
    # Allow any server administrators to kill the bottom
    await bot.close()
    print('Bot is logged out')


# Command !cap that can only be used by server administrators to change the node war cap
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def cap(ctx, capacity_setting):
    global NODE_CAPACITY
    global extra_list
    NODE_CAPACITY = capacity_setting
    # Attempt to empty out extra list onto the sheet
    try:
        for users in extra_list:
            if (check_todays_attendance_in_sheets(current_nw_weekday) <
                    int(NODE_CAPACITY)):
                update_cell(users, current_nw_weekday, 'TRUE')
                extra_list.remove(users)
    except IndexError:
        print("Cap changed, but extra list is empty")
    # Reply with message and new capacity set
    await ctx.channel.send('Node Cap: {}'.format(NODE_CAPACITY))


# Command !current will return the current node war size cap set
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def current(ctx):
    await ctx.channel.send('Current node cap: {}'.format(NODE_CAPACITY))


# Command !list will return the names of the people that have signed up but not reflected on the sheet
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def waitlist(ctx):
    for users in extra_list:
        print_list = users + ","
    if not extra_list:
        await ctx.channel.send('None')
    else:
        await ctx.channel.send('Extra members: {}'.format(print_list))


# Starts a command group for the help command
# Command groups will expand on a certain command such as help <command>
@bot.group(invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def help(ctx):
    embed_result = discord.Embed(
        title="Help",
        description=
        "Use !help <command> for extended information on a command.",
        color=ctx.author.color)
    embed_result.add_field(name="Moderation", value="kill")
    embed_result.add_field(name="Basic", value="cap, current, waitlist")

    await ctx.send(embed=embed_result)


# Part of help command group expand on the help command
# Will not return base help command, but will instead return declared embed
@help.command()
async def kill(ctx):
    embed_result = discord.Embed(title="kill",
                                 description="Kill the bot",
                                 color=ctx.author.color)

    await ctx.send(embed=embed_result)


# Part of help command group expand on the help command
# Will not return base help command, but will instead return declared embed
@help.command()
async def cap(ctx):
    embed_result = discord.Embed(
        title="cap",
        description=
        "Changes attendace capacity. If cap is increased, then it will automatically add all the people on waitlist",
        color=ctx.author.color)
    embed_result.add_field(name="**Syntax**", value="!cap <number>")

    await ctx.send(embed=embed_result)


@help.command()
async def current(ctx):
    embed_result = discord.Embed(
        title="current",
        description="Shows current node war cap size.",
        color=ctx.author.color)

    await ctx.send(embed=embed_result)


@help.command()
async def waitlist(ctx):
    embed_result = discord.Embed(
        title="waitlist",
        description=
        "Shows list of people beyond the node war cap that signed up. Returns list in chronological order (i.e. First on the list reacted first to announcement)",
        color=ctx.author.color)

    await ctx.send(embed=embed_result)


# Run bot
bot.run(TOKEN)
