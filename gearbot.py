import pickle
import json
import discord
from collections import defaultdict
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import validators

client = discord.Client()

GEARdict = defaultdict(list)

bdo_classes = ['warrior', 'valkyrie', 'valk', 'wizard', 'wiz', 'witch', 'ranger', 'sorceress', 'sorc', 'berserker', 'tamer', 'musa', 'maehwa', 'lahn', 'ninja', 'kunoichi', 'kuno', 'dk', 'DK', 'striker', 'mystic']
#missing check on eof and IOE
def write_gear_list():
    global GEARdict
    with open('gearlist', 'wb') as fp:
        pickle.dump(GEARdict, fp)
def read_gear_list():
    global GEARdict
    with open('gearlist', 'rb') as fp:
        GEARdict = pickle.load(fp)

async def is_officer(message): 
    if "maid" in [y.name.lower() for y in message.author.roles]: 
        return True

    return False

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(' ', scope)

gc = gspread.authorize(credentials)

sh = gc.open_by_url(" ") #sheet url here
wks = sh.worksheet("BOT") #replace with sheet tab name here

#reformat the message removing the bot prefix
def format_input(prefix,message):
    string = message.replace(prefix,'')
    string = string.lstrip()
    return string
#returns the key
def get_date(message):
    date = message.split(" ", 1)
    date = date[0]
    return date

#return the content of the msg 
def get_msg_content(message):
    content = message.split(" ", 1)
    content = content[1]
    return content

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    read_gear_list() #this will fail if gearlist file is empty or not there at all


@client.event
async def on_message(message):
    if message.content.startswith('!gear'):
        if message.channel.id == ' ': #change channel id here
            msg = format_input("!gear", message.content) #cleanup the message
            if message.mentions == []: #if there's no mentions it means you want to add/update gears otherwise pull the mentioned gear out
                msg_list = msg.split(" ",8) #split the msg in multiple args
                if(len(msg_list) == 8 and msg_list[2].isnumeric() and msg_list[3].lower() in bdo_classes and
                        msg_list[4].isnumeric() and msg_list[5].isnumeric() and
                        msg_list[6].isnumeric() and validators.url(msg_list[7])):
                    if(msg_list[7].endswith(".png") or msg_list[7].endswith(".jpg") ):
                        if msg: #forgot why it's here
                            if message.author.id in GEARdict.keys(): #if key is already there update it
                                del GEARdict[message.author.id]
                                GEARdict[message.author.id].append(msg_list[0]) #family n
                                GEARdict[message.author.id].append(msg_list[1]) #char n
                                GEARdict[message.author.id].append(msg_list[2]) #lvl
                                GEARdict[message.author.id].append(msg_list[3]) #class
                                GEARdict[message.author.id].append(msg_list[4]) #ap
                                GEARdict[message.author.id].append(msg_list[5]) #awaap
                                GEARdict[message.author.id].append(msg_list[6]) #dp
                                GEARdict[message.author.id].append(msg_list[7]) #pic
                                write_gear_list()
                                await client.send_message(message.channel,
                                                      "Your gear has been updated!")
                            else: #else add it anew
                                GEARdict[message.author.id].append(msg_list[0])
                                GEARdict[message.author.id].append(msg_list[1])
                                GEARdict[message.author.id].append(msg_list[2])
                                GEARdict[message.author.id].append(msg_list[3])
                                GEARdict[message.author.id].append(msg_list[4])
                                GEARdict[message.author.id].append(msg_list[5])
                                GEARdict[message.author.id].append(msg_list[6])
                                GEARdict[message.author.id].append(msg_list[7])
                                write_gear_list()
                                await client.send_message(message.channel,
                                                  "Your gear has been added ")
                    else:
                        await client.send_message(message.channel,
                                                  "Use a direct link to the picture (url must end with.png/.jpg) use ShareX it's free")
                else:
                    await client.send_message(message.channel, "Use !gear Family Character Lvl Class AP AWAAP DP Gear Pic link "
                                                               "(For Dark Knight use dk)")
            else:
                if msg:
                    id = message.mentions[0].id
                    for key in GEARdict:
                        if key == id:
                            userID = await client.get_user_info(key)
                            list = GEARdict[key]
                            if list[3] == 'dk':
                                bdoclass = 'Dark Knight'
                            elif list[3] == 'DK':
                                bdoclass = 'Dark Knight'
                            elif list[3] == 'valk':
                                bdoclass = 'Valkyrie'
                            elif list[3] == 'wizard':
                                bdoclass = 'Wizard'
                            elif list[3] == 'wiz':
                                bdoclass = 'Wizard' 
                            elif list[3] == 'sorc':
                                bdoclass = 'Sorceress'
                            elif list[3] == 'kuno':
                                bdoclass = 'Kunoichi' 
                            else:
                                bdoclass = list[3].title()                            
                            picurl = list[7].strip()
                            gs = int(((int(list[4]) + int(list[5])) / 2) + int(list[6]))
                            stringfix = list[1] + " " + list[0] + "**\nClass: **" + bdoclass + "**\nLvl: **"+ list[2] + "**\nGS: **" + str(gs)
                            classgs = stringfix.strip()
                            embed = discord.Embed()
                            embed.set_author(name=userID,icon_url=message.mentions[0].avatar_url)
                            embed.set_thumbnail(url=message.mentions[0].avatar_url)
                            embed.add_field(name=message.mentions[0].display_name,value=classgs,inline=False)
                            embed.set_image(url=picurl)
                            await client.send_message(message.channel,embed=embed)
                            break
                    else:
                       await client.send_message(message.channel,"Gear not found!")
                else:
                    await client.send_message(message.channel, "Use !gear + @someone!")


    elif message.content.startswith('!remove'):
        eval = await is_officer(message)
        if eval:
            id = message.mentions[0].id
            for key in GEARdict:
                if key == id:
                    del GEARdict[key]
                    write_gear_list()
                    await client.send_message(message.channel, "Gear has been removed")
                    break
            else:
                await client.send_message(message.channel, "Gear not found!")
        else:
            await client.send_message(message.channel,
                                      "You ain't a maid!")


    elif message.content.startswith('!rmid'): #remove gear by discord id
        eval = await is_officer(message)
        if eval:
            id = format_input("!rmid", message.content)
            for key in GEARdict:
                if key == id:
                    del GEARdict[key]
                    write_gear_list()
                    await client.send_message(message.channel, "Gear has been removed")
                    break
            else:
                await client.send_message(message.channel, "Gear not found!")
        else:
            await client.send_message(message.channel,
                                      "You ain't a maid!")


    elif message.content.startswith('!sheet'): #this is very hacky but it works 
        eval = await is_officer(message)
        if eval:
            i = 0
            gc.login() #refresh auth token
            cell_name_list = wks.range('A1:A100') #init enough lists to fill the sheet later
            cell_family_list = wks.range('B1:B100')
            cell_character_list = wks.range('C1:C100')
            cell_lvl_list = wks.range('D1:C100')
            cell_class_list = wks.range('E1:E100')
            cell_ap_list = wks.range('F1:F100')
            cell_awaap_list = wks.range('G1:G100')
            cell_dp_list = wks.range('H1:H100')
            cell_gearpic_list = wks.range('I1:I100')
            for key in GEARdict.fromkeys(GEARdict): #parse tru every key in the map and convert the id to real username then append it to the cell lists
                user = await client.get_user_info(key)
                new_key = user.name
                cell_name_list[i].value = new_key
                infos = GEARdict[key]
                cell_family_list[i].value = infos[0]
                cell_character_list[i].value = infos[1]
                cell_lvl_list[i].value = infos[2]
                cell_class_list[i].value = infos[3]
                cell_ap_list[i].value = infos[4]
                cell_awaap_list[i].value = infos[5]
                cell_dp_list[i].value = infos[6]
                cell_gearpic_list[i].value = infos[7]

                i += 1
            try: #write the lists to the sheet
                wks.update_cells(cell_name_list)
                wks.update_cells(cell_family_list)
                wks.update_cells(cell_character_list)
                wks.update_cells(cell_lvl_list)
                wks.update_cells(cell_class_list)
                wks.update_cells(cell_ap_list)
                wks.update_cells(cell_awaap_list)
                wks.update_cells(cell_dp_list)
                wks.update_cells(cell_gearpic_list)

                await client.send_message(message.channel, "Gear updated on the sheet!")
            except:
                await client.send_message(message.channel, "API Error") #most likely issues with the token
        else:  
            await client.send_message(message.channel,
                                      "You ain't a maid!")

    elif message.content.startswith('!check'): #self explanatory just counts how many entries we have got so far
        eval = await is_officer(message)
        if eval:
            i = 0
            for key in GEARdict.fromkeys(GEARdict):
                user = await client.get_user_info(key)
                i += 1
            else:
                await client.send_message(message.channel, "Number of users that submitted their gear: " + i)
        else:  
            await client.send_message(message.channel,
                                      "You ain't a maid!")


client.run('')#add your bot token here
