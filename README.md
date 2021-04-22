# AttendanceBot

> Discord bot that tracks reactions to message and adds it to Google Sheet worksheet. Allows the ability to cap reactions on Google Sheets.

## Table of contents

- [AttendanceBot](#attendancebot)
  - [Table of contents](#table-of-contents)
  - [General Info](#general-info)
  - [Technologies](#technologies)
  - [Setup](#setup)
  - [Features](#features)
  - [Contact](#contact)

## General Info

The need arose where tracking attendance for node wars in (Black Desert Online) BDO for certain node
sizes. The bot will track what the reaction of ✅.

Where ✅ means the an individual has the intention to show up for node war on given day.

## Technologies

Bot is created with:

- Python version: 3.8.5
- Python-dotenv version: 0.15.0
- Discord.py version: 1.5.1
- Google-api-python-client version: 2.1.0
- Gspread version: 3.6.0
- Schedule version: 1.1.0

## Setup

To run this bot, install these packages locally using pip:

```
$ pip install -r requirements.pip
```

Copy link https://discord.com/api/oauth2/authorize?client_id=747298773130149948&permissions=525440&scope=bot

Select your server and invite the bot.

**DON'T FORGET TO RESTRICT BOT TO THE CHANNEL YOU WANT TO KEEP ATTENDANCE**

## Features

List of current features in v2.1.3

- Keep track of ✅ reactions on discord only.
- Record reactions on Google Sheet using Google API v4.
- Command !cap changes the cap on the amount of reactions accepted by the bot.
- Reset cap command every day at 6pm PST.
- Search for names ignoring case and only returns whole word results
- Custom help command

## Contact

Created by [@Zwivix](https://github.com/Zwivee) - feel free to contact me!
