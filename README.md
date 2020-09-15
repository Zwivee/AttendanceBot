# AttendanceBot
> Discord bot that tracks reactions to message, and provides command to export json data to excel spreadsheet.

## Table of contents
- [AttendanceBot](#attendancebot)
  - [Table of contents](#table-of-contents)
  - [General Info](#general-info)
  - [Technologies](#technologies)
  - [Setup](#setup)
  - [Features](#features)
  - [Contact](#contact)


## General Info
The need arose where tracking attendance for node wars in BDO for certain node
sizes. The bot will track what the reaction of ✅ and 🪑.

Where ✅ means the person will show up for node wars, and 🪑 meaning they can
show but are okay with being 'benched'.

## Technologies
Bot is created with:
* Discord.py version: 1.5.0a
* Pandas version: 0.24.2
* Python version: 3.5.2


## Setup
To run this bot, install these packages locally using pip:
```
$ pip install python
$ pip install pandas
```
Copy link https://discord.com/oauth2/authorize?client_id=747298773130149948&scope=bot

Select your server and invite the bot.

**DON'T FORGET TO RESTRICT BOT TO THE CHANNEL YOU WANT TO KEEP ATTENDANCE**

## Features
List of current features in v1.0
* Keep track of ✅ and 🪑 reactions on discord only.
* Produces excel spreadsheet on root directory.
* Command !attendance will generate excel spreadsheet.

## Contact
Created by [@Zwivix](https://github.com/Zwivee) - feel free to contact me!
