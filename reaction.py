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


# Bot started
@bot.event
async def on_ready():
    print("Bot is logged in.")


# Name of user that added reacted to message
def get_user(user):
    new_person = user.display_name
    pattern = '''"([^"]*)"'''
    in_game_name = re.findall(pattern, new_person, re.IGNORECASE)
    result = in_game_name[0]
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
    NODE_CAPACITY = capacity_setting

    # Reply with message and new capacity set
    await ctx.channel.send('Node Cap: {}'.format(NODE_CAPACITY))


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def current(ctx):
    await ctx.channel.send('Current node cap: {}'.format(NODE_CAPACITY))


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def list(ctx):
    for users in extra_list:
        print_list = users + ","
    if not extra_list:
        await ctx.channel.send('None')
    else:
        await ctx.channel.send('Extra members: {}'.format(print_list))


# Starts a command group for the help command
# Command groups will expand on a certain command such as help <command>
@bot.group(invoke_without_command=True)
async def help(ctx):
    embed_result = discord.Embed(
        title="Help",
        description=
        "Use !help <command> for extended information on a command.",
        color=ctx.author.color)
    embed_result.add_field(name="Moderation", value="Kill")
    embed_result.add_field(name="Basic", value="Cap")

    await ctx.send(embed=embed_result)


# Part of help command group expand on the help command
# Will not return base help command, but will instead return declared embed
@help.command()
async def kill_help(ctx):
    embed_result = discord.Embed(title="kill",
                                 description="Kill the bot",
                                 color=ctx.author.color)

    await ctx.send(embed=embed_result)


# Part of help command group expand on the help command
# Will not return base help command, but will instead return declared embed
@help.command()
async def cap_help(ctx):
    embed_result = discord.Embed(title="cap",
                                 description="Changes attendace capacity.",
                                 color=ctx.author.color)
    embed_result.add_field(name="**Syntax**", value="!cap <number>")

    await ctx.send(embed=embed_result)


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
@tasks.loop(hours=NODE_CAPACITY_RESET_TIMER)
async def reset_capacity():
    await asyncio.sleep(
        seconds_until(HOUR_OF_DAY_TO_RESET, MINUTE_OF_HOUR_TO_RESET))
    global NODE_CAPACITY
    NODE_CAPACITY = MAX_ATTENDANCE
    print('Node Capacity Reset')


reset_capacity.start()

# Run bot
bot.run(TOKEN)
