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
            replyMessage = replyMessage + ".saveLoot lootText          - Will save loot to a file on the server, very useful if you don't want to manually save everything locally\n"
            replyMessage = replyMessage + ".calcSavedLoot              - Will calculate all the payout from loot saved to the saveLoot file on the server\n"
            replyMessage = replyMessage + ".clearSavedLoot             - Will clear all the prior saved loot from the server\n"
            replyMessage = replyMessage + ".calcLoot lootText          - Will calculate the payouts from the lootText you provide the command\n"
            replyMessage = replyMessage + ".charInfo name              - Will show information about the player name specified\n"
            replyMessage = replyMessage + ".deathList name             - Will show all deaths of the player name specified\n"
            replyMessage = replyMessage + ".vocStats ED/RP/MS/EK level - Will display general stats for the vocation and specified level\n"
            replyMessage = replyMessage + ".whoIsOwner?                - Will display who is the assigned owner of the current bot instance\n"
            replyMessage = replyMessage + ".github?                    - Will display the link to my github containing the project for this bot\n"
            replyMessage = replyMessage + ".upTime S/M/H/D             - Will display the current time elapsed since bot restarted (S = seconds, M = minutes, H = hours, D = days)\n"
            replyMessage = replyMessage + ".spell spellname            - Will display information about the spell name you are looking up```"
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
            print(spellName)
            response = requests.get('https://tibiawiki.dev/api/spells/{0}'.format(spellName))
            if response.status_code == 200:
                response = response.json()
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
                replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nFailed to fetch information from api```"
            print("{0} executed spell lookup command".format(message.author))
            await message.channel.send(replyMessage)

        if message.content.startswith('.spells '):
            removePrefix = message.content.split('.spells ')
            if removePrefix[0] == ' ':
                del removePrefix[0]
            if "knight" in removePrefix[1].lower() or "paladin" in removePrefix[1].lower() or "druid" in removePrefix[1].lower() or "sorcerer" in removePrefix[1].lower():
                await message.channel.send("Please give me a moment to fetch this data from the api")
                response = requests.get('https://tibiawiki.dev/api/spells?expand=true')
                if response.status_code == 200:
                    response = response.json()
                    spellList = list()
                    for i in response:
                        if "voc" in i:
                            if removePrefix[1].lower() in i["voc"].lower():
                                print(i["name"])
                                spellList.append(i["name"])
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Spell List for the vocation you specified***\n'
                    for i in spellList:
                        replyMessage = replyMessage + '{0}\n'.format(i)
                    replyMessage = replyMessage + '\nInformation provided by: https://tibiawiki.dev/api```'
                else:
                    replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nFailed to fetch information from api```"
            else:
                replyMessage = '<@{}>'.format(message.author.id) + "```***Error***\nVocation not recognized```"
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