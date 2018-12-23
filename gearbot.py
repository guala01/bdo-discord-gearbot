"""
gearbot for blackdesert online/mmo games with discord and google sheet implementation
the bot will keep all the information in a hasmap which gets dumped in a serialized pickle file for backup reason
the sheet gets also updated automatically, adjust cells and row offsets at the beginning and if not using a default setup
(starting row and col 1) or if you have empty cells as header please update the find_and_update and the find_next_row function
accordingly
"""

import pickle
import json
import os
import discord
from collections import defaultdict
import gspread
import asyncio
from oauth2client.service_account import ServiceAccountCredentials
import validators

client = discord.Client()

GEARdict = defaultdict(list)

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('.json', scope)

gc = gspread.authorize(credentials)

sh = gc.open_by_url("") #sheet url here
wks = sh.worksheet("Sheet2") #replace with sheet tab name here

cell_name_list = wks.range('A2:A100') #init enough lists to fill the sheet later
cell_family_list = wks.range('B2:B100')
cell_character_list = wks.range('C2:C100')
cell_lvl_list = wks.range('D2:D100')
cell_class_list = wks.range('E2:E100')
cell_ap_list = wks.range('F2:F100')
cell_awaap_list = wks.range('G2:G100')
cell_dp_list = wks.range('H2:H100')
cell_gearpic_list = wks.range('I2:I100')

bdo_classes = ['archer','warrior', 'valkyrie', 'valk', 'wizard', 'wiz', 'witch', 'ranger', 'sorceress', 'sorc', 'berserker', 'tamer', 'musa', 'maehwa', 'lahn', 'ninja', 'kunoichi', 'kuno', 'dk', 'DK', 'striker','stroker', 'mystic']
#missing check on eof and IOE
def write_gear_list():
    global GEARdict
    with open('gearlist', 'wb') as fp:
        pickle.dump(GEARdict, fp)
def read_gear_list():
    global GEARdict
    try:
        with open('gearlist', 'rb') as fp:
            GEARdict = pickle.load(fp)
    except IOError: #no file
        fp = open('gearlist', 'w+')
        GEARdict = defaultdict(list)
    except EOFError: #file empty
        GEARdict = defaultdict(list)

async def is_officer(message): 
    if "maids" in [y.name.lower() for y in message.author.roles]: 
        return True

    return False

async def is_member(member): 
    if "members" in [y.name.lower() for y in member.roles]: 
        return True

    return False

#reformat the message removing the bot prefix
def format_input(prefix,message):
    string = message.replace(prefix,'')
    string = string.lstrip()
    return string
#returns the key
def get_key(message):
    key = message.split(" ", 1)
    key = key[0]
    return key

#return the content of the msg 
def get_msg_content(message):
    content = message.split(" ", 1)
    content = content[1]
    return content

async def msg_validation(msg_list,message,offset):
    if(len(msg_list) == 8+offset and msg_list[2+offset].isnumeric() and msg_list[3+offset].lower() in bdo_classes and
        msg_list[4+offset].isnumeric() and msg_list[5+offset].isnumeric() and
        msg_list[6+offset].isnumeric()):
        return True
    else:
        await show_help(message)
        return False

async def url_validation(msg_list,message,offset):
    if((msg_list[7+offset].lower().endswith(".png") or msg_list[7+offset].lower().endswith(".jpg")) and validators.url(msg_list[7+offset])):
        return True
    else:
        await client.send_message(message.channel,
                                                    "Use a direct link to the picture (url must end with.png/.jpg) use ShareX it's free")
        return False

async def show_help(message):
    embed = discord.Embed()
    embed.set_author(name="Gear Help",icon_url=client.user.avatar_url)
    embed.set_thumbnail(url=client.user.avatar_url)
    embed.add_field(name="How To Add Your Gear",value="!gear Family(name) Character(name) Level Class AP AWAAP DP Gear Picture Link",inline=False)
    embed.add_field(name="Classes Rules",value="For Dark Knight use dk",inline=False)
    embed.add_field(name="Gear Pic Rules",value="Use a direct link to the picture(url must end with .jpg/.png)use ShareX, it's free",inline=False)
    embed.add_field(name="See Gear",value="Use !gear +@someone",inline=False)
    embed.add_field(name="Gear Update",value="Use !update stats + ap + dp + gear link",inline=False)
    embed.add_field(name="Level Update",value="Use !update level + new level",inline=False)
    await client.send_message(message.channel,embed=embed)

def class_check(class_name):
    if class_name == 'DK':
        bdoclass = 'Dark Knight'
    elif class_name == 'dk':
        bdoclass = 'Dark Knight'
    elif class_name == 'valk':
        bdoclass = 'Valkyrie'
    elif class_name == 'wizard':
        bdoclass = 'Wizard'
    elif class_name == 'wiz':
        bdoclass = 'Wizard' 
    elif class_name == 'sorc':
        bdoclass = 'Sorceress'
    elif class_name == 'kuno':
        bdoclass = 'Kunoichi' 
    elif class_name == 'stroker':
        bdoclass = 'Striker'
    else:
        bdoclass = class_name.title()
    return bdoclass

def delete_from_sheet(name):
    gc.login()
    try:
        cell = wks.find(name)
        wks.delete_row(cell.row)
        print("deleted")
    except:
        print("not found on sheet, wrong fam name ?")

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

async def find_and_update(message,user):
    gc.login()
    id = user.id
    infos = GEARdict[id]
    #user = await client.get_user_info(id)
    name = user.display_name
    bdoclass = class_check(infos[3])
    try:
        cell = wks.find(infos[0]) #find fam name in sheet which is at col 2
        column = cell.col
        if (column == 1): #fam name same as discord name ?
            column = column+1
            print("same discord name as fam name")
        print("user found in sheet")
        try: #write the lists to the sheet
            wks.update_cell(cell.row,column-1,name)
            wks.update_cell(cell.row,column,infos[0])
            wks.update_cell(cell.row,column+1,infos[1])
            wks.update_cell(cell.row,column+2,infos[2])
            wks.update_cell(cell.row,column+3,bdoclass)
            wks.update_cell(cell.row,column+4,infos[4])
            wks.update_cell(cell.row,column+5,infos[5])
            wks.update_cell(cell.row,column+6,infos[6])
            wks.update_cell(cell.row,column+7,infos[7])
        except:
            await client.send_message(message.channel,"Something went wrong while updating the sheet, please inform my cute master")
            return
    except:
        next_row = next_available_row(wks)
        print("add new user")
        try: #write the lists to the sheet
            wks.update_cell(next_row,1,name)
            wks.update_cell(next_row,2,infos[0])
            wks.update_cell(next_row,3,infos[1])
            wks.update_cell(next_row,4,infos[2])
            wks.update_cell(next_row,5,bdoclass)
            wks.update_cell(next_row,6,infos[4])
            wks.update_cell(next_row,7,infos[5])
            wks.update_cell(next_row,8,infos[6])
            wks.update_cell(next_row,9,infos[7])
        except:
            await client.send_message(message.channel,"Something went wrong while adding a new slave, please inform my cute master")
    
async def send_timed_msg(message,embed,timer):
    await client.wait_until_ready()
    msg = await client.send_message(message.channel,embed=embed )
    await asyncio.sleep(timer) 
    await client.delete_message(msg)

async def show_gear_embed(message,picurl,classgs,userID):
    embed = discord.Embed()
    embed.set_author(name=userID,icon_url=message.mentions[0].avatar_url)
    embed.set_thumbnail(url=message.mentions[0].avatar_url)
    embed.add_field(name=message.mentions[0].display_name,value=classgs,inline=False)
    embed.set_image(url=picurl)
    #await send_timed_msg(message,embed,15) #timed message example
    await client.send_message(message.channel,embed=embed)

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
        if message.channel.id == '465920848738385920': #change channel id here
            msg = format_input("!gear", message.content) #cleanup the message
            if msg: #empty message
                if message.mentions == []: #if there's no mentions it means you want to add/update gears otherwise pull the mentioned gear out
                    msg_list = msg.split(" ",8) #split the msg in multiple args
                    if await msg_validation(msg_list,message,0) and await url_validation(msg_list,message,0):
                            if message.author.id in GEARdict.keys(): #if key is already there update it
                                del GEARdict[message.author.id]
                                for i in range(8):
                                    GEARdict[message.author.id].append(msg_list[i])
                                    #0 fam n 1 char n 2 lvl 3 class 4 ap 5  awap 6 dp 7 pic
                                await find_and_update(message,message.author)
                                write_gear_list()
                                await client.send_message(message.channel,
                                                        "Gear updated, remember that you can use !update to update your gear instead")
                            else: #else add it anew
                                for j in range(8):
                                    GEARdict[message.author.id].append(msg_list[j])
                                await find_and_update(message,message.author)
                                write_gear_list()
                                await client.send_message(message.channel,
                                                    "Gear submitted!")
                else:
                    if msg: #show gear
                        id = message.mentions[0].id
                        for key in GEARdict:
                            if key == id:
                                userID = await client.get_user_info(key)
                                list = GEARdict[key]
                                bdoclass = class_check(list[3])                            
                                picurl = list[7].strip()
                                gs = int(((int(list[4]) + int(list[5])) / 2) + int(list[6]))
                                stringfix = list[1] + " " + list[0] + "**\nClass: **" + bdoclass + "**\nLvl: **"+ list[2] + "**\nGS: **" + str(gs)
                                classgs = stringfix.strip()
                                await show_gear_embed(message,picurl,classgs,userID)
                                break
                        else:
                            await client.send_message(message.channel,"Gear not found!")
            else:
                await show_help(message)

    elif message.content.startswith('!remove'):
        eval = await is_officer(message)
        if eval:
            if not message.mentions:
                id = format_input("!remove", message.content)
                if id in GEARdict.keys():
                    member = await client.get_user_info(id)
                    discord_name = member.display_name
                    list = GEARdict[id]
                    name = list[0]
                    delete_from_sheet(name)
                    del GEARdict[id]
                    write_gear_list()
                    await client.send_message(message.channel, "{} gear has been moved to Bless Online".format(discord_name))
                else:
                    await client.send_message(message.channel, "Use !remove +@someone or ID to remove his gear")
            else:    
                if message.mentions[0].id in GEARdict.keys():
                    list = GEARdict[message.mentions[0].id]
                    name = list[0]
                    delete_from_sheet(name)
                    del GEARdict[message.mentions[0].id]
                    write_gear_list()
                    await client.send_message(message.channel, "{} gear has been removed!".format(message.mentions[0].display_name))
                else:
                    await client.send_message(message.channel, "Gear not found!")
        else:
            await client.send_message(message.channel,
                                      "I don't think so!")

    elif message.content.startswith('!update'):
        if message.channel.id == '465920848738385920':
            msg = format_input("!update", message.content)
            msg_list = msg.split(" ",1)
            msg_list[0] = msg_list[0].lower()
            print("msg_list: ",msg_list)
            if message.author.id in GEARdict.keys():
                if msg_list[0] == 'stats':
                    stats_list = msg_list[1].split(" ",4)
                    print("stats_list: ",stats_list)
                    if (len(stats_list) == 4 and stats_list[0].isnumeric() and 
                        stats_list[1].isnumeric() and stats_list[2].isnumeric() and validators.url(stats_list[3])):
                        if(stats_list[3].lower().endswith(".png") or stats_list[3].lower().endswith(".jpg") ):
                            GEARdict[message.author.id].pop(4)
                            GEARdict[message.author.id].insert(4,stats_list[0]) #ap
                            GEARdict[message.author.id].pop(5)
                            GEARdict[message.author.id].insert(5,stats_list[1]) #awaap
                            GEARdict[message.author.id].pop(6)
                            GEARdict[message.author.id].insert(6,stats_list[2]) #dp
                            GEARdict[message.author.id].pop(7)
                            GEARdict[message.author.id].insert(7,stats_list[3]) #link
                            await find_and_update(message,message.author)
                            write_gear_list()
                            await client.send_message(message.channel,
                                                        "Gear updated!")
                        else:
                            await client.send_message(message.channel,
                                                    "Use a direct link to the picture (url must end with.png/.jpg), use ShareX it's free!")
                    else:
                        await show_help(message)
                elif msg_list[0] == 'level':
                    level_list = msg_list[1].split(" ",2)
                    print("level: ",level_list)
                    if(level_list[0].isnumeric()):
                        GEARdict[message.author.id].pop(2)
                        GEARdict[message.author.id].insert(2,level_list[0])
                        await find_and_update(message,message.author)
                        write_gear_list()
                        await client.send_message(message.channel,
                                                    "How to waste your life 101 by {}".format(message.author.display_name))  
                else:
                    await show_help(message)
            else:
                       await client.send_message(message.channel,"You should submit your gear first!")

    elif message.content.startswith('!check'): #self explanatory just counts how many entries we have got so far
        eval = await is_officer(message)
        if eval:
            i = 0
            for key in GEARdict.fromkeys(GEARdict):
                i += 1
            else:
                await client.send_message(message.channel, "Number of slaves that submitted to me thus far: " + str(i))
        else:  
            await client.send_message(message.channel,
                                      "What are you trying to do ? Time to take out the whip")

    elif message.content.startswith('!help'): 
        await show_help(message)
    
    elif message.content.startswith('!slackers'):
        eval = await is_officer(message)
        if eval:
            m_list = message.server.members
            await client.send_message(message.channel,"What is this trash")
            for members in m_list:
                check = await is_member(members)
                if check:
                    if members.id not in GEARdict.keys():
                        await client.send_message(message.channel,"" + members.mention)
        else:
            await client.send_message(message.channel,
                                      "Listen here you little shit")

    elif message.content.startswith('!fsupdate'):
        if message.channel.id == '465920848738385920':
            eval = await is_officer(message)
            if eval:
                if message.mentions:
                    id = message.mentions[0].id
                    print(id)
                    msg = format_input("!fsupdate", message.content)
                    print("msg1: {}".format(msg))
                    try:
                        msg_list = msg.split(" ",2)
                        msg_list[1] = msg_list[1].lower()
                        print("msg_list: ",msg_list)
                        if id in GEARdict.keys():
                            #user = await client.get_user_info(id)
                            if msg_list[1] == 'stats':
                                stats_list = msg_list[2].split(" ",4)
                                print("stats_list: ",stats_list)
                                if (len(stats_list) == 4 and stats_list[0].isnumeric() and 
                                    stats_list[1].isnumeric() and stats_list[2].isnumeric() and validators.url(stats_list[3])):
                                    if(stats_list[3].lower().endswith(".png") or stats_list[3].lower().endswith(".jpg") ):
                                        GEARdict[id].pop(4)
                                        GEARdict[id].insert(4,stats_list[0]) #ap
                                        GEARdict[id].pop(5)
                                        GEARdict[id].insert(5,stats_list[1]) #awaap
                                        GEARdict[id].pop(6)
                                        GEARdict[id].insert(6,stats_list[2]) #dp
                                        GEARdict[id].pop(7)
                                        GEARdict[id].insert(7,stats_list[3]) #link
                                        await find_and_update(message,message.mentions[0])
                                        write_gear_list()
                                        await client.send_message(message.channel,
                                                                    "Forcefully updated his gear!")
                                    else:
                                        await client.send_message(message.channel,
                                                                "Not a direct link or invalid url! Url must end with.png/.jpg")
                                else:
                                    await show_help(message)
                            elif msg_list[1] == 'level':
                                level = msg_list[2]
                                print("level: ",level)
                                if(level.isnumeric()):
                                    GEARdict[id].pop(2)
                                    GEARdict[id].insert(2,level)
                                    await find_and_update(message,message.mentions[0])
                                    write_gear_list()
                                    await client.send_message(message.channel,
                                                                "Level forcefully updated")  
                            else:
                                await client.send_message(message.channel,"Wrong sintax, !fsupdate @someone stats/level")
                        else:
                            await client.send_message(message.channel,"Gear not found!")
                    except:
                        await client.send_message(message.channel,"Wrong sintax, !fsupdate @someone stats/level")
                else:
                    await client.send_message(message.channel,"You are not mentioning anyone are you drunk again or just stupid?")    

    elif message.content.startswith('!dmslackers'):
        eval = await is_officer(message)
        if eval:
            m_list = message.server.members
            await client.send_message(message.channel,"On it! Check your dms for the list!") 
            await client.send_message(message.author,"Sent a message to:")
            for members in m_list:
                check = await is_member(members)
                if check:
                    if members.id not in GEARdict.keys():
                        await client.send_message(members,"Kind reminder to submit your gear, or weird action will be taken! https://b.catgirlsare.sexy/hRvs.gif ")
                        await client.send_message(message.author,"{}".format(members.display_name))                    
        else:
            await client.send_message(message.channel,
                                      "Are you THAT stupid ?")

    elif message.content.startswith('!manual'):
        eval = await is_officer(message)
        if message.channel.id == '465920848738385920' and eval: #change channel id here
            msg = format_input("!manual", message.content) #cleanup the message
            if msg: #check for empty msg
                if message.mentions: #if there's no mentions it means you want to add/update gears otherwise pull the mentioned gear out
                    msg_list = msg.split(" ",9) #split the msg in multiple args
                    if await msg_validation(msg_list,message,1) and await url_validation(msg_list,message,1):
                        if message.mentions[0].id in GEARdict.keys(): #if key is already there update it
                            del GEARdict[message.mentions[0].id]
                            for i in range(1,9):
                                GEARdict[message.mentions[0].id].append(msg_list[i])
                                #0 fam n 1 char n 2 lvl 3 class 4 ap 5  awap 6 dp 7 pic
                            await find_and_update(message,message.mentions[0])
                            write_gear_list()
                            await client.send_message(message.channel,
                                                    "Why are you doing this, are you aware that you can use !fsupdate ? Whatever I'll let this pass")
                        else: #else add it anew
                            for j in range(1,9):
                                GEARdict[message.mentions[0].id].append(msg_list[j])
                            await find_and_update(message,message.mentions[0])
                            write_gear_list()
                            await client.send_message(message.channel,
                                                "Added a new slave to the pack")
                    else:
                        print("message validation failed")
                else:
                    print("mention not found")
            else:
                print("empty msg")
                
client.run('')#add your bot token here
