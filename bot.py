import discord
import datetime
import os
import requests
import json
import sys
import time
from locale import atoi, setlocale, LC_NUMERIC

setlocale(LC_NUMERIC, 'en_US.UTF8')
client = discord.Client()

weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

botOwner = None
setPassword = False
rootPassword = ''
pauseBot = False
changeOwner = False
restartedBot = False
restartCommandChannel = ""
savedGuildID = 0
restartTime = 0

startTime = time.time()

print("Checking for any root users")

curPath = os.path.dirname(sys.argv[0])

if not os.path.exists(os.path.join(os.path.dirname(sys.argv[0]), "servers")):
    print("There is no directory called servers")
    os.mkdir(os.path.join(os.path.dirname(sys.argv[0]), "servers"))

if os.path.exists("rootUser.txt"):
    with open("rootUser.txt", 'r') as f:
        rootUserText = ""
        for line in f.readlines():
            rootUserText = rootUserText + line
        if len(rootUserText) > 1:
            splitRootUserText = rootUserText.split(' ')
            botOwner = int(splitRootUserText[0])
            rootPassword = splitRootUserText[1]
    
if botOwner:
    print("Root user found! ID: {0}".format(botOwner))
    print("Root password: {0}".format(rootPassword))
else:
    print("No root user found!")

if os.path.exists("restartBot.txt"):
    with open("restartBot.txt", 'r') as f:
        restartBotText = ""
        for line in f.readlines():
            restartBotText = restartBotText + line
        if len(restartBotText) > 1:
            splitRestartBotText = restartBotText.split(' ')
            if splitRestartBotText[0] == "TRUE":
                restartedBot = True
                restartCommandChannel = splitRestartBotText[1]
                savedGuildID = int(splitRestartBotText[2])
                restartTime = float(splitRestartBotText[3])

@client.event
async def on_ready():
    global restartedBot
    global restartCommandChannel
    global restartTime

    print('Connected as {0.user}'.format(client))
    # If bot was restarted
    if restartedBot:
        guild = client.get_guild(savedGuildID)
        channel = discord.utils.get(guild.text_channels, name=restartCommandChannel)
        if os.path.exists("restartBot.txt"):
            os.remove("restartBot.txt")
            restartedBot = False
            restartCommandChannel = ""
        await channel.send("Bot restarted successfully! (Duration: {0} seconds)".format(round(time.time() - restartTime, 2)))
    for guild in client.guilds:
        if not os.path.exists(os.path.join(curPath, "servers", str(guild.id))):
            os.mkdir(os.path.join(curPath, "servers", str(guild.id)))

@client.event
async def on_message(message):
    global botOwner
    global setPassword
    global rootPassword
    global pauseBot
    global changeOwner
    global restartedBot
    global restartCommandChannel
    global startTime

    if message.author == client.user:
        return

    if message.content.startswith('.adminHelp') and rootPassword in message.content:
        replyMessage = '<@{}>'.format(message.author.id)
        replyMessage = replyMessage + "```***Help / Commands for owner***\n"
        replyMessage = replyMessage + ".setRootAccess ID         - Assign owner and root access to a user (preferably the owner)\n"
        replyMessage = replyMessage + ".restartBot               - Restart the bot, will take a few seconds. Don't forget to include root password if you're not the assigned owner\n"
        replyMessage = replyMessage + ".pauseBot                 - Paus the bot from responding to commands, will still respond to root commands\n"
        replyMessage = replyMessage + ".resumeBot                - Unpause the bot from responding to commands\n"
        replyMessage = replyMessage + ".changeOwner              - Will change the owner to another user\n"
        replyMessage = replyMessage + ".setRootPassword OLD NEW  - Will set a new root password\n"
        replyMessage = replyMessage + ".giveRootPassword         - Will send you the root password if you're the assigned owner```"
        print("{0} executed admin help commands".format(message.author))
        await message.channel.send(replyMessage)
    elif message.content.startswith('.adminHelp'):
        replyMessage = '<@{}>'.format(message.author.id)
        replyMessage = replyMessage + "```***Error***\nDon't forget to include the root password to execute this command```"
        await message.channel.send(replyMessage)

    # Root access to bot
    if setPassword and message.author.id == botOwner:
        rootPassword = message.content
        setPassword = False
        with open("rootUser.txt", 'w') as f:
            f.write(str(botOwner) + " " + rootPassword)
        await message.channel.send("Password successfully set!")

    if message.content.startswith('.setRootAccess ') and not botOwner:
        removePrefix = message.content.split('.setRootAccess ')
        if removePrefix[0] == ' ':
            del removePrefix[0]
        botOwner = int(removePrefix[1])
        setPassword = True
        replyMessage = '<@{}>'.format(message.author.id) + '```'
        replyMessage = replyMessage + 'Root access set to {0} \n'.format(botOwner)
        replyMessage = replyMessage + "Please enter desired root password after this response```"
        print("{0} executed set root access command".format(message.author))
        await message.channel.send(replyMessage) 
      
    if message.content.startswith('.pauseBot') and (message.author.id == botOwner or rootPassword in message.content):
        pauseBot = True
        print("{0} executed pause bot command".format(message.author))
        await message.channel.send("Bot paused!")

    if message.content.startswith('.resumeBot') and (message.author.id == botOwner or rootPassword in message.content):
        pauseBot = False
        print("{0} executed unpause bot command".format(message.author))
        await message.channel.send("Bot unpaused!")

    if message.content.startswith('.changeOwner') and message.author.id == botOwner:
        changeOwner = True
        replyMessage = '<@{}>'.format(message.author.id) + '```'
        replyMessage = replyMessage + 'Enter desires userID for the new owner after this response```'
        print("{0} executed change owner command".format(message.author))
        await message.channel.send(replyMessage)

    if changeOwner and message.author.id == botOwner:
        botOwner = int(message.content)
        changeOwner = False
        if os.path.exists("rootUser.txt"):
            print("User cleared from server file")
            os.remove("rootUser.txt")
        with open("rootUser.txt", 'w') as f:
            print("User updated in server file")
            f.write(str(botOwner) + " " + rootPassword)
        user = client.get_user(botOwner)
        await user.send('Current root password is: {0}\n To change this use the command .setRootPassword OLD NEW').format(rootPassword)

    if message.content.startswith('.setRootPassword ') and message.author.id == botOwner:
        removePrefix = message.content.split('.setRootPassword ')
        if removePrefix[0] == ' ':
            del removePrefix[0]
        splitRemovePrefix = removePrefix[1].split(' ')
        rootPassword = splitRemovePrefix[1]
        if os.path.exists("rootUser.txt"):
            print("Password cleared from server file")
            os.remove("rootUser.txt")
        with open("rootUser.txt", 'w') as f:
            print("Password updated in server file")
            f.write(str(botOwner) + " " + rootPassword)
        replyMessage = '<@{}>'.format(message.author.id) + '```'
        replyMessage = replyMessage + 'Root password successfully changed to {0}```'.format(rootPassword)
        print("{0} executed set root password command".format(message.author))
        await message.author.send(replyMessage)
    
    if message.content.startswith('.giveRootPassword') and (message.author.id == botOwner or rootPassword in message.content):
        print("{0} executed give root password command".format(message.author))
        if not message.author.id == botOwner:
            await message.author.send("Password sent to the root user")
        await message.author.send("The root password is: {0}".format(rootPassword))

    if message.content.startswith('.restartBot') and (message.author.id == botOwner or rootPassword in message.content):
        if os.path.exists("restartBot.txt"):
            os.remove("restartBot.txt")
        with open("restartBot.txt", 'w') as f:
            print("Saved channel and guild")
            f.write("TRUE " + message.channel.name + " " + str(message.guild.id) + " " + str(time.time()))
        await message.channel.send("Please wait a moment as I restart! Be right back!")
        os.execv(sys.executable, ['python3'] + sys.argv)
    elif message.content.startswith('.restartBot'):
        await message.channel.send("You lack permissions to execute a restart! Please provide the root password or become owner of the bot")
    # End of root access

    # List all commands and explanation for the command
    if not pauseBot:
        if message.content.startswith('.help'):
            replyMessage = '<@{}>'.format(message.author.id)
            replyMessage = replyMessage + "```***Help / Commands***\n"
            replyMessage = replyMessage + ".rashid?                    - Will let you know what city Rashid is currently reciding in, BOT DOES NOT ACCOUNT FOR SERVER SAVE\n"
            replyMessage = replyMessage + ".shareExp level             - Will let you know what the party exp share range is for your level\n"
            replyMessage = replyMessage + ".saveLoot lootText          - Will save loot to a user specific file on the server to later be calculated using the '.calcSavedLoot' command\n"
            replyMessage = replyMessage + ".calcSavedLoot              - Will calculate all the payout from loot saved to the user specific saveLoot file on the server\n"
            replyMessage = replyMessage + ".clearSavedLoot             - Will clear all the prior saved loot from the server\n"
            replyMessage = replyMessage + ".calcLoot lootText          - Will calculate the payouts from the lootText you provide the command\n"
            replyMessage = replyMessage + ".charInfo name              - Will show information about the player name specified\n"
            replyMessage = replyMessage + ".deathList name             - Will show all deaths of the player name specified\n"
            replyMessage = replyMessage + ".vocStats ED/RP/MS/EK level - Will display general stats for the vocation and specified level\n"
            replyMessage = replyMessage + ".whoIsOwner?                - Will display who is the assigned owner of the current bot instance\n"
            replyMessage = replyMessage + ".github?                    - Will display the link to my github containing the project for this bot\n"
            replyMessage = replyMessage + ".upTime S/M/H/D             - Will display the current time elapsed since bot restarted (S = seconds, M = minutes, H = hours, D = days)\n"
            replyMessage = replyMessage + ".spell spellname            - Will display information about the spell name you are looking up\n"
            replyMessage = replyMessage + ".spells vocation            - Will display all spells for the specified vocation\n"
            replyMessage = replyMessage + ".item itemname              - Will display information about the item you are looking up\n"
            replyMessage = replyMessage + ".creature creaturename      - Will display information about the creature you are looking up```"
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
            if splitString[0] == "EK":
                level = int(splitString[1])
                speed = 117 + level - 8
                cap = 470 + (25 * (level - 8))
                hp = 185 + (15 * (level - 8))
                mana = 90 + (5 * (level - 8))
                replyMessage = '<@{}>'.format(message.author.id) + '```***General Vocation Stats For EK***\n'
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
            if not os.path.exists(os.path.join(curPath, "servers", str(message.guild.id), str(message.author.id))):
                if not os.path.exists(os.path.join(curPath, "servers", str(message.guild.id))):
                    os.mkdir(os.path.join(curPath, "servers", str(message.guild.id)))
                else:
                    os.mkdir(os.path.join(curPath, "servers", str(message.guild.id), str(message.author.id)))    
            with open(os.path.join(curPath, "servers", str(message.guild.id), str(message.author.id), "savedLoot.txt"), "a+") as f:
                f.write(removePrefix[1] + "\n")
            replyMessage = '<@{}>'.format(message.author.id) + '```***Save Loot***\n Successfully saved loot to server```'
            print("{0} executed save loot".format(message.author))
            await message.channel.send(replyMessage)

        if message.content.startswith('.calcSavedLoot'):
            players = {}
            entries = 0
            if os.path.exists(os.path.join(curPath, "servers", str(message.guild.id), str(message.author.id))):
                with open(os.path.join(curPath, "servers", str(message.guild.id), str(message.author.id), "savedLoot.txt"), "r") as f:
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
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Payout from {0} hunt(s)***'.format(entries)
                    for k, sendMessage in players.items():
                        replyMessage = replyMessage + '\n'
                        replyMessage = replyMessage + k + ': ' + str(sendMessage)
                    replyMessage = replyMessage + '```'
            else:
                replyMessage = '<@{}>'.format(message.author.id) + '```***Calc Saved Loot***\n Failed to read saved loot file```'
            print("{0} executed saved loot calculator".format(message.author))
            await message.channel.send(replyMessage)

        if message.content.startswith('.clearSavedLoot'):
            if os.path.exists(os.path.join(curPath, "servers", str(message.guild.id), str(message.author.id))):
                os.remove(os.path.join(curPath, "servers", str(message.guild.id), str(message.author.id), "savedLoot.txt"))
            replyMessage = '<@{}>'.format(message.author.id) + '```***Clear Saved Loot***\n Successfully cleared saved loot```'
            await message.channel.send(replyMessage)

        if message.content.startswith(".charInfo "):
            removePrefix = message.content.split('.charInfo ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            tempMessage = await message.channel.send("Please give me a moment to fetch this data from the api")
            charInfo = requests.get("https://api.tibiadata.com/v2/characters/{0}.json".format(removePrefix[1][0].upper() + removePrefix[1][1:]), verify=False)
            if charInfo.status_code == 200:
                errorOccured = False
                for i in charInfo.json()["characters"]:
                    if "error" in i:
                        errorOccured = True
                if not errorOccured:
                    charInfoData = charInfo.json()["characters"]["data"]
                    lastLoginDate = charInfoData["last_login"][0]["date"][:-7]
                    lastLoginTimezone = charInfoData["last_login"][0]["timezone"]
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Character info***\n'
                    replyMessage = replyMessage + "Name: {0}\n".format(charInfoData["name"])
                    replyMessage = replyMessage + "Level: {0}\n".format(charInfoData["level"])
                    replyMessage = replyMessage + "Vocation: {0}\n".format(charInfoData["vocation"])
                    replyMessage = replyMessage + "Status: {0}\n".format(charInfoData["status"])
                    replyMessage = replyMessage + "Last login: {0} {1}\n".format(lastLoginDate, lastLoginTimezone)
                    replyMessage = replyMessage + "\nLast API update: {0}\n".format(charInfo.json()["information"]["last_updated"].split(" ")[1])
                    replyMessage = replyMessage + 'Information provided by: https://api.tibiadata.com/v2/```'
                else:
                    replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nPlease provide a valid character name```"
            else:
                replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nFailed to fetch information from api```"
            await tempMessage.edit(content=replyMessage)

        if message.content.startswith(".deathList "):
            removePrefix = message.content.split('.deathList ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            tempMessage = await message.channel.send("Please give me a moment to fetch this data from the api")
            charInfo = requests.get("https://api.tibiadata.com/v2/characters/{0}.json".format(removePrefix[1]), verify=False)
            if charInfo.status_code == 200:
                errorOccured = False
                for i in charInfo.json()["characters"]:
                    if "error" in i:
                        errorOccured = True
                if not errorOccured:
                    charInfoData = charInfo.json()["characters"]["deaths"]
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Deathlist***\n'
                    for death in charInfoData:
                        replyMessage = replyMessage + "Date: {0}\n".format(death["date"]["date"].split(" ")[0])
                        replyMessage = replyMessage + "Level: {0}\n".format(death["level"])
                        replyMessage = replyMessage + "Reason: {0}\n".format(death["reason"])
                        replyMessage = replyMessage + "\n"
                    replyMessage = replyMessage + "\nLast API update: {0}\n".format(charInfo.json()["information"]["last_updated"].split(" ")[1])
                    replyMessage = replyMessage + 'Information provided by: https://api.tibiadata.com/v2/```'
                else:
                    replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nPlease provide a valid character name```"
            else:
                replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nFailed to fetch information from api```"
            await tempMessage.edit(content=replyMessage)
        
        if message.content.startswith('.whoIsOwner?'):
            replyMessage = '<@{}>'.format(message.author.id) + '```***Owner***\n'
            if botOwner:
                user = client.get_user(botOwner)
                replyMessage = replyMessage + '{0} is the owner```'.format(user.name)
            else:
                replyMessage = replyMessage + 'No one is assigned owner```'
            await message.channel.send(replyMessage)
        if message.content.startswith('.github?'):
            replyMessage = '<@{}>'.format(message.author.id)
            replyMessage = replyMessage + "\nThis bot is open-source and available here: https://github.com/Frowsty/TibiaDiscordBot"
            await message.channel.send(replyMessage)

        if message.content.startswith('.upTime '):
            removePrefix = message.content.split(' ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            didFindUnit = False
            replyMessage = '<@{}>'.format(message.author.id) + '```***Uptime***\n'
            if removePrefix[1].upper() == 'S':
                replyMessage = replyMessage + "Current uptime is: {0} seconds```".format(round(time.time() - startTime, 2))
                didFindUnit = True
            if removePrefix[1].upper() == 'M':
                replyMessage = replyMessage + "Current uptime is: {0} minutes```".format(round(int(time.time() - startTime) / 60, 2))
                didFindUnit = True
            if removePrefix[1].upper() == 'H':
                replyMessage = replyMessage + "Current uptime is: {0} hours```".format(round(int(time.time() - startTime) / 3600, 2))
                didFindUnit = True
            if removePrefix[1].upper() == 'D':
                replyMessage = replyMessage + "Current uptime is: {0} days```".format(round(int(time.time() - startTime) / 86400, 2))
                didFindUnit = True
            if not didFindUnit:
                replyMessage = replyMessage + "You forgot to specify the unit of which time should be presented in. Please use S/M/H/D after the command. Example '.upTime S'```"
            print("{0} executed uptime command".format(message.author))
            await message.channel.send(replyMessage)

        if message.content.startswith('.spell '):
            removePrefix = message.content.split('.spell ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            splitSpellName = removePrefix[1].split()
            spellName = ""
            num = 0
            for i in splitSpellName:
                num = num + 1
                if num < len(splitSpellName):
                    spellName = spellName + i.capitalize() + "%20"
                else:
                    spellName = spellName + i.capitalize()
            response = requests.get('https://tibiawiki.dev/api/spells/{0}'.format(spellName))
            if response.status_code == 200:
                response = response.json()
                if response["templateType"] == "Spell":
                    vocText = response["voc"]
                    vocText = vocText.replace("[", "")
                    vocText = vocText.replace("]", "")
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Spell Info***\n'
                    replyMessage = replyMessage + 'Name: {0}\n'.format(response["name"])
                    replyMessage = replyMessage + 'Level: {0}\n'.format(response["levelrequired"])
                    replyMessage = replyMessage + 'Mana Cost: {0}\n'.format(response["mana"])
                    replyMessage = replyMessage + 'Vocation(s): {0}\n'.format(vocText)
                    replyMessage = replyMessage + 'Spell Cost: {0}\n'.format(response["spellcost"])
                    replyMessage = replyMessage + 'Spell Type: {0}\n'.format(response["subclass"])
                    if response["subclass"] == "Attack":
                        replyMessage = replyMessage + 'Damage Type: {0}\n'.format(response["damagetype"])
                    replyMessage = replyMessage + 'Spell Words: {0}\n\n'.format(response["words"])
                    replyMessage = replyMessage + 'Information provided by: https://tibiawiki.dev/api```'
                else:
                    replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nPlease provide a valid spell name```"
            else:
                replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nFailed to fetch information from api```"
            print("{0} executed spell lookup command".format(message.author))
            await message.channel.send(replyMessage)

        if message.content.startswith('.spells '):
            removePrefix = message.content.split('.spells ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            tempMessage = await message.channel.send("Please give me a moment to fetch this data from the api")
            if "knight" in removePrefix[1].lower() or "paladin" in removePrefix[1].lower() or "druid" in removePrefix[1].lower() or "sorcerer" in removePrefix[1].lower():
                response = requests.get('https://tibiawiki.dev/api/spells?expand=true')
                if response.status_code == 200:
                    response = response.json()
                    spellList = list()
                    for i in response:
                        if "voc" in i:
                            if removePrefix[1].lower() in i["voc"].lower():
                                print(i["name"])
                                spellList.append(i["name"])
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Spell List ({0})***\n'.format(removePrefix[1].lower())
                    for i in spellList:
                        replyMessage = replyMessage + '{0}\n'.format(i)
                    replyMessage = replyMessage + '\nInformation provided by: https://tibiawiki.dev/api```'
                else:
                    replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nFailed to fetch information from api```"
            else:
                replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nVocation not recognized```"
            print("{0} executed spell list command".format(message.author))
            await tempMessage.edit(content=replyMessage)

        if message.content.startswith('.item '):
            removePrefix = message.content.split('.item ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            splitItemName = removePrefix[1].split()
            itemName = ""
            num = 0
            for i in splitItemName:
                num = num + 1
                if num < len(splitItemName):
                    if i.lower() == "of":
                        itemName = itemName + i + "%20"
                    else:
                        itemName = itemName + i.capitalize() + "%20"
                else:
                    itemName = itemName + i.capitalize()
            tempMessage = await message.channel.send("Please wait while I fetch this information!")
            response = requests.get('https://tibiawiki.dev/api/items/{0}'.format(itemName))
            displayImbues = False
            displayDefMod = False
            displayAttrib = False
            displayResist = False
            displayVoc = False
            displayLevelReq = False
            displayEnergyAtk = False
            displayFireAtk = False
            displayIceAtk = False
            displayEarthAtk = False
            displayDeathAtk = False
            displayManaLeech = False
            displayHpLeech = False
            displayAttack = False
            displayDefense = False
            displayDamageType = False
            displayDamage = False
            displayCrit = False
            displayCharges = False
            displayManaCost = False
            displayArmor = False
            displayDuration = False
            displayVolume = False
            displayHands = False
            displayAttackMod = False
            displayHitMod = False
            displayRange = False

            if response.status_code == 200 and len(response.json()) > 1:
                response = response.json()
                if response["templateType"] == "Item":
                    for i in response:
                        if "armor" in i:
                            displayArmor = True
                        if "attack" in i:
                            displayAttack = True
                        if "defense" in i:
                            displayDefense = True
                        if "vocrequired" in i:
                            displayVoc = True
                        if "resist" in i:
                            displayResist = True
                        if "attrib" in i:
                            displayAttrib = True
                        if "defensemod" in i:
                            displayDefMod = True
                        if "energy_attack" in i:
                            displayEnergyAtk = True
                        if "imbueslots" in i:
                            displayImbues = True
                        if "levelrequired" in i:
                            displayLevelReq = True
                        if "fire_attack" in i:
                            displayFireAtk = True
                        if "ice_attack" in i:
                            displayIceAtk = True
                        if "earth_attack" in i:
                            displayEarthAtk = True
                        if "death_attack" in i:
                            displayDeathAtk = True
                        if "manaleech_am" in i or "manaleech_ch" in i:
                            displayManaLeech = True
                        if "hpleech_am" in i or "hpleech_ch" in i:
                            displayHpLeech = True
                        if "damagetype" in i:
                            displayDamageType = True
                        if "damage" in i:
                            displayDamage = True
                        if "crithit_ch" in i:
                            displayCrit = True
                        if "charges" in i:
                            displayCharges = True
                        if "mana" == i:
                            displayManaCost = True
                        if "duration" in i:
                            displayDuration = True
                        if "volume" in i:
                            displayVolume = True
                        if "hands" in i:
                            displayHands = True
                        if "atk_mod" in i:
                            displayAttackMod = True
                        if "hit_mod" in i:
                            displayHitMod = True
                        if "range" in i:
                            displayRange = True

                    replyMessage = '<@{}>'.format(message.author.id) + '```***Item Info***\n'
                    replyMessage = replyMessage + 'Name: {0}\n'.format(response["name"])
                    if response["itemclass"] == "Weapons":
                        if displayAttack:
                            replyMessage = replyMessage + 'Attack: {0}\n'.format(response["attack"])
                        if displayDamage:
                            replyMessage = replyMessage + 'Damage: {0}\n'.format(response["damage"])
                        if displayDamageType:
                            replyMessage = replyMessage + 'Damage Type: {0}\n'.format(response["damagetype"])
                        if displayAttackMod:
                            replyMessage = replyMessage + 'Attack Mod: +{0}\n'.format(response["atk_mod"])
                        if displayHitMod:
                            replyMessage = replyMessage + 'Hit Mod: {0}%\n'.format(response["hit_mod"])
                        if displayRange:
                            replyMessage = replyMessage + 'Range: {0}\n'.format(response["range"])
                        if displayEnergyAtk:
                            replyMessage = replyMessage + 'Energy Damage: {0}\n'.format(response["energy_attack"])
                        if displayFireAtk:
                            replyMessage = replyMessage + 'Fire Damage: {0}\n'.format(response["fire_attack"])
                        if displayIceAtk:
                            replyMessage = replyMessage + 'Ice Damage: {0}\n'.format(response["ice_attack"])
                        if displayEarthAtk:
                            replyMessage = replyMessage + 'Earth Damage: {0}\n'.format(response["earth_attack"])
                        if displayDeathAtk:
                            replyMessage = replyMessage + 'Death Damage: {0}\n'.format(response["death_attack"])
                        if displayDefense:
                            replyMessage = replyMessage + 'Defense: {0}\n'.format(response["defense"])
                        if displayHands:
                            replyMessage = replyMessage + 'Hands: {0}\n'.format(response["hands"])
                        if displayImbues:
                            replyMessage = replyMessage + 'Imbue Slots: {0}\n'.format(response["imbueslots"])
                        if displayVoc:
                            replyMessage = replyMessage + 'Required Vocation: {0}\n'.format(response["vocrequired"])
                        if displayResist:
                            replyMessage = replyMessage + 'Protection: {0}\n'.format(response["resist"])
                        if displayAttrib:
                            replyMessage = replyMessage + 'Attributes: {0}\n'.format(response["attrib"])
                        if displayManaLeech:
                            replyMessage = replyMessage + 'Mana leech Chance/Amount: {0} / {1}\n'.format(response["manaleech_ch"], response["manaleech_am"])
                        if displayHpLeech:
                            replyMessage = replyMessage + 'Life leech Chance/Amount: {0} / {1}\n'.format(response["hpleech_ch"], response["hpleech_am"])
                        if displayCrit:
                            replyMessage = replyMessage + 'Critical hit Chance/Amount: {0} / {1}\n'.format(response["crithit_ch"], response["critextra_dmg"])
                        if displayCharges:
                            replyMessage = replyMessage + 'Charges: {0}\n'.format(response["charges"])
                        if displayManaCost:
                            replyMessage = replyMessage + 'Mana per hit: {0}\n'.format(response["mana"])
                        if displayDefMod:
                            replyMessage = replyMessage + 'Defence Mod: {0}\n'.format(response["defensemod"])
                        if displayLevelReq:
                            replyMessage = replyMessage + 'Level Requirement: {0}\n'.format(response["levelrequired"])
                    if response["itemclass"] == "Body Equipment":
                        if displayArmor:
                            replyMessage = replyMessage + 'Armor: {0}\n'.format(response["armor"])
                        if displayImbues:
                            replyMessage = replyMessage + 'Imbue Slots: {0}\n'.format(response["imbueslots"])
                        if displayResist:
                            replyMessage = replyMessage + 'Protection: {0}\n'.format(response["resist"])
                        if displayAttrib:
                            replyMessage = replyMessage + 'Attributes: {0}\n'.format(response["attrib"])
                        if displayVoc:
                            replyMessage = replyMessage + 'Required Vocation: {0}\n'.format(response["vocrequired"])
                        if displayLevelReq:
                            replyMessage = replyMessage + 'Level Requirement: {0}\n'.format(response["levelrequired"])
                    if response["itemclass"] == "Tools and other Equipment":
                        if displayArmor:
                            replyMessage = replyMessage + 'Armor: {0}\n'.format(response["armor"])
                        if displayResist:
                            replyMessage = replyMessage + 'Protection: {0}\n'.format(response["resist"])
                        if displayAttrib:
                            replyMessage = replyMessage + 'Attributes: {0}\n'.format(response["attrib"])
                        if displayDuration:
                            replyMessage = replyMessage + 'Duration: {0}\n'.format(response["duration"])
                        if displayCharges:
                            replyMessage = replyMessage + 'Charges: {0}\n'.format(response["charges"])
                        if displayVoc:
                            replyMessage = replyMessage + 'Required Vocation: {0}\n'.format(response["vocrequired"])
                        if displayLevelReq:
                            replyMessage = replyMessage + 'Level Requirement: {0}\n'.format(response["levelrequired"])
                    if response["itemclass"] == "Household Items" or response["itemclass"] == "Other Items":
                        if displayVolume:
                            replyMessage = replyMessage + 'Volume: {0}\n'.format(response["volume"])
                        if displayImbues:
                            replyMessage = replyMessage + 'Imbue Slots: {0}\n'.format(response["imbueslots"])
                    replyMessage = replyMessage + 'Weight: {0}\n'.format(response["weight"])
                    replyMessage = replyMessage + 'Value: {0}\n'.format(response["value"])
                    replyMessage = replyMessage + 'NPC Value: {0}\n'.format(response["npcvalue"])
                    replyMessage = replyMessage + '\nInformation provided by: https://tibiawiki.dev/api```'
                else:
                    replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nPlease provide a valid item name```"
            else:
                replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nFailed to fetch information from api```"
            print("{0} executed item lookup command".format(message.author))
            await tempMessage.edit(content=replyMessage)

        if message.content.startswith('.creature '):
            removePrefix = message.content.split('.creature ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            splitCreatureName = removePrefix[1].split()
            creatureName = ""
            num = 0
            for i in splitCreatureName:
                num = num + 1
                if num < len(splitCreatureName):
                    if i.lower() == "of":
                        creatureName = creatureName + i + "%20"
                    else:
                        creatureName = creatureName + i.capitalize() + "%20"
                else:
                    creatureName = creatureName + i.capitalize()
            tempMessage = await message.channel.send("Please wait while I fetch this information")
            response = requests.get('https://tibiawiki.dev/api/creatures/{0}'.format(creatureName))
            if response.status_code == 200:
                response = response.json()
                displayHpDrainMod = False
                displayHealMod = False
                displayFireDmgMod = False
                displayHolyDmgMod = False
                displayEarthDmgMod = False
                displayPhysicalDmgMod = False
                displayDrownDmgMod = False
                displayIceDmgMod = False
                displayEnergyDmgMod = False
                displayDeathDmgMod = False
                displayIsBoss = False
                displayMaxDmg = False
                displayPushObjects = False
                displayWalksThrough = False
                displayParaImmune = False
                displaySenseInvis = False
                displayExperience = False

                if response["templateType"] == "Creature":
                    for i in response:
                        if "walksthrough" in i:
                            displayWalksThrough = True
                        if "pushobjects" in i:
                            displayPushObjects = True
                        if "maxdmg" in i:
                            displayMaxDmg = True
                        if "isboss" in i:
                            displayIsBoss = True
                        if "drownDmgMod" in i:
                            displayDrownDmgMod = True
                        if "holyDmgMod" in i:
                            displayHolyDmgMod = True
                        if "physicalDmgMod" in i:
                            displayPhysicalDmgMod = True
                        if "energyDmgMod" in i:
                            displayEnergyDmgMod = True
                        if "earthDmgMod" in i:
                            displayEarthDmgMod = True
                        if "iceDmgMod" in i:
                            displayIceDmgMod = True
                        if "deathDmgMod" in i:
                            displayDeathDmgMod = True
                        if "hpDrainDmgMod" in i:
                            displayHpDrainMod = True
                        if "healMod" in i:
                            displayHealMod = True
                        if "fireDmgMod" in i:
                            displayFireDmgMod = True
                        if "paraimmune" in i:
                            displayParaImmune = True
                        if "senseinvis" in i:
                            displaySenseInvis = True
                        if "exp" in i:
                            displayExperience = True
                    
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Creature Info***\n'
                    replyMessage = replyMessage + 'Name: {0}\n'.format(response["name"])
                    replyMessage = replyMessage + 'Health: {0}\n'.format(response["hp"])
                    replyMessage = replyMessage + 'Experience: {0}\n'.format(response["exp"])
                    if displayMaxDmg:
                        replyMessage = replyMessage + 'Max Damage: {0}\n'.format(response["maxdmg"])
                    if displayIsBoss:
                        replyMessage = replyMessage + 'Is Boss?: {0}\n'.format(response["isboss"])
                    if displayPushObjects:
                        replyMessage = replyMessage + 'Push objects?: {0}\n'.format(response["pushobjects"])
                    if displayWalksThrough:
                        replyMessage = replyMessage + 'Walks Through: {0}\n'.format(response["walksthrough"])
                    replyMessage = replyMessage + '-Elemental Properties-\n'
                    if displayPhysicalDmgMod:
                        replyMessage = replyMessage + 'Physical: {0}\n'.format(response["physicalDmgMod"])
                    if displayEarthDmgMod:
                        replyMessage = replyMessage + 'Earth: {0}\n'.format(response["earthDmgMod"])
                    if displayFireDmgMod:
                        replyMessage = replyMessage + 'Fire: {0}\n'.format(response["fireDmgMod"])
                    if displayDeathDmgMod:
                        replyMessage = replyMessage + 'Death: {0}\n'.format(response["deathDmgMod"])
                    if displayEnergyDmgMod:
                        replyMessage = replyMessage + 'Energy: {0}\n'.format(response["energyDmgMod"])
                    if displayHolyDmgMod:
                        replyMessage = replyMessage + 'Holy: {0}\n'.format(response["holyDmgMod"])
                    if displayIceDmgMod:
                        replyMessage = replyMessage + 'Ice: {0}\n'.format(response["iceDmgMod"])
                    if displayHealMod:
                        replyMessage = replyMessage + 'Heal: {0}\n'.format(response["healMod"])
                    if displayHpDrainMod:
                        replyMessage = replyMessage + 'Life Drain: {0}\n'.format(response["hpDrainDmgMod"])
                    if displayDrownDmgMod:
                        replyMessage = replyMessage + 'Drown: {0}\n'.format(response["drownDmgMod"])
                    replyMessage = replyMessage + '-Immunity Properties-\n'
                    if displayParaImmune:
                        replyMessage = replyMessage + 'Paralysable: {0}\n'.format(response["paraimmune"])
                    if displaySenseInvis:
                        replyMessage = replyMessage + 'Sense Invisible: {0}\n'.format(response["senseinvis"])
                    replyMessage = replyMessage + '\nInformation provided by: https://tibiawiki.dev/api```'
                else:
                    replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nPlease provide a valid creature name```"
            else:
                replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nFailed to fetch information from api```"
            print("{0} executed creature lookup command".format(message.author))
            await tempMessage.edit(content=replyMessage)

        if message.content.startswith('.addHunted '):
            removePrefix = message.content.split('.addHunted ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            if not os.path.exists(os.path.join(curPath, "servers", str(message.guild.id))):
                os.mkdir(os.path.join(curPath, "servers", str(message.guild.id)))
            with open(os.path.join(curPath, "servers", str(message.guild.id), "huntedList.txt"), "a+") as f:
                f.write(removePrefix[1] + "\n")
            replyMessage = '<@{}>'.format(message.author.id) + '```***Hunted List***\n Players successfully added to hunted list```'
            print("{0} executed add hunted command".format(message.author))
            await message.channel.send(replyMessage)

        if message.content.startswith('.huntedList'):
            replyMessage = '<@{}>'.format(message.author.id) + '```***Hunted List***\n'
            if os.path.exists(os.path.join(curPath, "servers", str(message.guild.id), "huntedList.txt")):
                with open(os.path.join(curPath, "servers", str(message.guild.id), "huntedList.txt"), "r") as f:
                    for i in f.readlines():
                        replyMessage = replyMessage + i
            else:
                replyMessage = replyMessage + "No hunted list found"
            replyMessage = replyMessage + "```"
            print("{0} executed hunted list command".format(message.author))
            await message.channel.send(replyMessage)
        
        if message.content.startswith('.removeHunted '):
            removePrefix = message.content.split('.removeHunted ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            storeFileInfo = ""
            wasFound = False
            if os.path.exists(os.path.join(curPath, "servers", str(message.guild.id), "huntedList.txt")):
                replyMessage = '<@{}>'.format(message.author.id) + '```***Hunted List***\n'
                with open(os.path.join(curPath, "servers", str(message.guild.id), "huntedList.txt"), "r") as f:
                    for i in f.readlines():
                        if not removePrefix[1] in i:
                            storeFileInfo = storeFileInfo + i
                        else:
                            wasFound = True
                with open(os.path.join(curPath, "servers", str(message.guild.id), "huntedList.txt"), "w") as f:
                    f.write(storeFileInfo)
                if wasFound:
                    replyMessage = replyMessage + "Successfully removed played from hunted list```"
            else:
                replyMessage = '<@{}>'.format(message.author.id) + '```***Hunted List***\n Hunted list not found```'
            print("{0} executed remove hunted command".format(message.author))
            await message.channel.send(replyMessage)

botToken = ""
if os.path.exists("token.txt"):
    with open("token.txt", 'r') as f:
        botToken = f.readline()

if botToken:
    print("Bot token found inside token.txt, launching bot!")
    client.run(botToken)
else:
    print("Bot token not found, exiting bot!")