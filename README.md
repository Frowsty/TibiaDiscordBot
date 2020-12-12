# TibiaDiscordBot

This repository contains the source-code of the discord bot "TibiaBotTools"
This started as a fun little single file discord bot project containing a handfull of useful features

My idea was to create a bot that makes life easier for tibia players. We all have discord at this point,
wouldn't it be great to search up information about a character with a simple command rather than having
to enter the website and search the name manually on the website? That's where this bot makes your life easier.
With simple commands you can get necessary info to continue your tibia adventure.

# Current features

- Look up player (.charInfo NAME)
  - Will look up the player through the TibiaData API
  - Displays general info such as Name, Level, Vocation, Online status
- Party share exp calculator (.shareExp LEVEL)
  - Will calculate the minimum and maximum exp share range for the specified level
- Rashid finder (.rashid?)
  - Will show where rashid is currently recided
- Vocation stats (.vocStats EK/RP/ED/MS LEVEL)
  - Will display general stats for the specified vocation and level
  - The following stats will be shown: speed, cap, health, mana 

# LOOT RELATED COMMANDS ARE GLOBALLY STORED ON THE SERVER, IT IS NOT SERVER SPECIFIC THEREFOR IF YOU WANT TO USE THOSE YOU MUST DEPLOY THIS BOT ON YOUR OWN SERVER
  
