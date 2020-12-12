import discord
import datetime
import os
import requests
import json
from locale import atoi, setlocale, LC_NUMERIC

setlocale(LC_NUMERIC, 'en_US.UTF8')
client = discord.Client()

weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

@client.event
async def on_ready():
    print('Connected as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # List all commands and explanation for the command
    if message.content.startswith('.help'):
        replyMessage = '<@{}>'.format(message.author.id)
        replyMessage = replyMessage + "```***HELP / COMMANDS***\n"
        replyMessage = replyMessage + ".rashid?                    - Will let you know what city Rashid is currently reciding in, BOT DOES NOT ACCOUNT FOR SERVER SAVE\n"
        replyMessage = replyMessage + ".shareExp level             - Will let you know what the party exp share range is for your level\n"
        replyMessage = replyMessage + ".saveLoot lootText          - Will save loot to a file on the server, very useful if you don't want to manually save everything locally\n"
        replyMessage = replyMessage + ".calcSavedLoot              - Will calculate all the payout from loot saved to the saveLoot file on the server\n"
        replyMessage = replyMessage + ".clearSavedLoot             - Will clear all the prior saved loot from the server\n"
        replyMessage = replyMessage + ".calcLoot lootText          - Will calculate the payouts from the lootText you provide the command\n"
        replyMessage = replyMessage + ".charInfo name              - Will show information about the player name specified\n"
        replyMessage = replyMessage + ".deathList name             - Will show all deaths of the player name specified\n"
        replyMessage = replyMessage + ".vocStats ED/RP/MS/EK level - Will display general stats for the vocation and specified level```"
        print("{0} executed help command".format(message.author))
        await message.channel.send(replyMessage)

    # Calculate total profits each player should get by using certain syntax
    if message.content.startswith('.calcLoot '):
        players = {}
        removePrefix = message.content.split('.calcLoot ')
        if removePrefix[0] == ' ':
            del removePrefix[0]
        removeTitle = removePrefix[1].split('Hunt loot share: \n')
        if removeTitle[0] == ' ':
            del removeTitle[0]
        for msg in removeTitle:
            splitMsg = msg.split('\n')
            for m in splitMsg:
                splitM = m.split(': ')
                if len(splitM) > 1:
                    if splitM[0] in players:
                        players[splitM[0]] = players[splitM[0]] + atoi(splitM[1])
                    else:
                        players[splitM[0]] = 0
                        players[splitM[0]] = players[splitM[0]] + atoi(splitM[1])
        replyMessage = '<@{}>'.format(message.author.id) + '```***Payouts***'
        for k, sendMessage in players.items():
            replyMessage = replyMessage + '\n'
            replyMessage = replyMessage + k + ': ' + str(sendMessage)
        replyMessage = replyMessage + '```'
        print("{0} executed loot calculator".format(message.author))
        await message.channel.send(replyMessage)

    # Tibia party exp share range calculator
    if message.content.startswith('.shareExp '):
        removePrefix = message.content.split('.shareExp ')
        if removePrefix[0] == ' ':
            del removePrefix[0]
        level = atoi(removePrefix[1])
        minLevel = level * (2/3)
        maxLevel = level * 2
        while (maxLevel * (2/3) - level) > 0:
            maxLevel = maxLevel - 1
        replyMessage = '<@{}>'.format(message.author.id) + '```***Exp Share Range***\n'
        replyMessage = replyMessage + 'MIN: {0}\nMAX: {1}'.format(int(minLevel), int(maxLevel + 1)) + '```'
        print("{0} executed share exp checker".format(message.author))
        await message.channel.send(replyMessage)

    # Check general stats for vocations and their level
    if message.content.startswith('.vocStats '):
        removePrefix = message.content.split('.vocStats ')
        if removePrefix[0] == ' ':
            del removePrefix[0]
        splitString = removePrefix[1].split(" ")
        replyMessage = ""
        if splitString[0] == "ED" or splitString[0] == "MS":
            level = int(splitString[1])
            speed = 117 + level - 8
            cap = 470 + (10 * (level - 8))
            hp = 185 + (5 * (level - 8))
            mana = 90 + (30 * (level - 8))
            replyMessage = '<@{}>'.format(message.author.id) + '```***General Vocation Stats For ED/MS***\n'
            replyMessage = replyMessage + 'HP: {0}\nMANA: {1}\nCAP: {2}\nSPEED: {3}'.format(hp, mana, cap, speed) + '```'
        if splitString[0] == "EK":
            level = int(splitString[1])
            speed = 117 + level - 8
            cap = 470 + (25 * (level - 8))
            hp = 185 + (15 * (level - 8))
            mana = 90 + (5 * (level - 8))
            replyMessage = '<@{}>'.format(message.author.id) + '```***General Vocation Stats For EK***\n'
            replyMessage = replyMessage + 'HP: {0}\nMANA: {1}\nCAP: {2}\nSPEED: {3}'.format(hp, mana, cap, speed) + '```'
        if splitString[0] == "RP":
            level = int(splitString[1])
            speed = 117 + level - 8
            cap = 470 + (20 * (level - 8))
            hp = 185 + (10 * (level - 8))
            mana = 90 + (15 * (level - 8))
            replyMessage = '<@{}>'.format(message.author.id) + '```***General Vocation Stats For RP***\n'
            replyMessage = replyMessage + 'HP: {0}\nMANA: {1}\nCAP: {2}\nSPEED: {3}'.format(hp, mana, cap, speed) + '```'
        print("{0} executed vocation stats checker".format(message.author))
        await message.channel.send(replyMessage)

    if message.content.startswith('.rashid?'):
        current_date = datetime.datetime.now()
        current_date.strftime('%A')
        replyMessage = '<@{}>'.format(message.author.id) + '```***Rashids Position***\n'
        replyMessage = replyMessage + 'After server-save at 10:00 CET Rashid will be in '
        weekday = datetime.date(current_date.year, current_date.month, current_date.day).weekday() 
        if weekDays[weekday] == "Monday":
            replyMessage = replyMessage + 'Svargrond```'
        if weekDays[weekday] == "Tuesday":
            replyMessage = replyMessage + 'Liberty Bay```'
        if weekDays[weekday] == "Wednesday":
            replyMessage = replyMessage + 'Port Hope```'
        if weekDays[weekday] == "Thursday":
            replyMessage = replyMessage + 'Ankrahmun```'
        if weekDays[weekday] == "Friday":
            replyMessage = replyMessage + 'Darashia```'
        if weekDays[weekday] == "Saturday":
            replyMessage = replyMessage + 'Edron```'
        if weekDays[weekday] == "Sunday":
            replyMessage = replyMessage + 'Carlin```'
        print("{0} executed where is rashid".format(message.author))
        await message.channel.send(replyMessage)

    if message.content.startswith('.saveLoot '):
        removePrefix = message.content.split('.saveLoot ')
        if removePrefix[0] == ' ':
            del removePrefix[0]
        with open("savedLoot.txt", "a+") as f:
            f.write(removePrefix[1] + "\n")
        replyMessage = '<@{}>'.format(message.author.id) + '```***Save Loot***\n Successfully saved loot to server```'
        print("{0} executed save loot".format(message.author))
        await message.channel.send(replyMessage)

    if message.content.startswith('.calcSavedLoot'):
        players = {}
        entries = 0
        if os.path.exists("savedLoot.txt"):
            with open("savedLoot.txt", "r") as f:
                lootText = ""
                for line in f.readlines():
                    if line == "Hunt loot share: \n":
                        entries = entries + 1
                    lootText = lootText + line
                removeTitle = lootText.split('Hunt loot share: \n')
                if removeTitle[0] == ' ':
                    del removeTitle[0]
                for msg in removeTitle:
                    splitMsg = msg.split('\n')
                    for m in splitMsg:
                        splitM = m.split(': ')
                        if len(splitM) > 1:
                            if splitM[0] in players:
                                players[splitM[0]] = players[splitM[0]] + atoi(splitM[1])
                            else:
                                players[splitM[0]] = 0
                                players[splitM[0]] = players[splitM[0]] + atoi(splitM[1])
                replyMessage = '<@{}>'.format(message.author.id) + '```***Payouts from {0} hunt(s)***'.format(entries)
                for k, sendMessage in players.items():
                    replyMessage = replyMessage + '\n'
                    replyMessage = replyMessage + k + ': ' + str(sendMessage)
                replyMessage = replyMessage + '```'
        else:
            replyMessage = '<@{}>'.format(message.author.id) + '```***Calc Saved Loot***\n Failed to read saved loot file```'
        print("{0} executed saved loot calculator".format(message.author))
        await message.channel.send(replyMessage)

    if message.content.startswith('.clearSavedLoot'):
        if os.path.exists("savedLoot.txt"):
            os.remove("savedLoot.txt")
        replyMessage = '<@{}>'.format(message.author.id) + '```***Clear Saved Loot***\n Successfully cleared saved loot```'
        await message.channel.send(replyMessage)

    if message.content.startswith(".charInfo "):
        removePrefix = message.content.split('.charInfo ')
        if removePrefix[0] == ' ':
            del removePrefix[0]
        charInfo = requests.get("https://api.tibiadata.com/v2/characters/{0}.json".format(removePrefix[1]))
        charInfoData = charInfo.json()["characters"]["data"]
        if charInfo.status_code == 200:
            replyMessage = '<@{}>'.format(message.author.id) + '```***Character info***\n'
            replyMessage = replyMessage + "Name: {0}\n".format(charInfoData["name"])
            replyMessage = replyMessage + "Level: {0}\n".format(charInfoData["level"])
            replyMessage = replyMessage + "Vocation: {0}\n".format(charInfoData["vocation"])
            replyMessage = replyMessage + "Status: {0}\n".format(charInfoData["status"])
            replyMessage = replyMessage + "Last API update: {0}```".format(charInfo.json()["information"]["last_updated"].split(" ")[1])
            await message.channel.send(replyMessage)

    if message.content.startswith(".deathList "):
        removePrefix = message.content.split('.deathList ')
        if removePrefix[0] == ' ':
            del removePrefix[0]
        charInfo = requests.get("https://api.tibiadata.com/v2/characters/{0}.json".format(removePrefix[1]))
        charInfoData = charInfo.json()["characters"]["deaths"]
        if charInfo.status_code == 200:
            replyMessage = '<@{}>'.format(message.author.id) + '```***Deathlist***\n'
            for death in charInfoData:
                replyMessage = replyMessage + "Date: {0}\n".format(death["date"]["date"].split(" ")[0])
                replyMessage = replyMessage + "Level: {0}\n".format(death["level"])
                replyMessage = replyMessage + "Reason: {0}\n".format(death["reason"])
                replyMessage = replyMessage + "\n"
            replyMessage = replyMessage + "```"
            await message.channel.send(replyMessage)
client.run("Something here")
