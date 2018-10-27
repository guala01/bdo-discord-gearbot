import pickle
import json
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

credentials = ServiceAccountCredentials.from_json_keyfile_name('', scope)#add json credentials file name

gc = gspread.authorize(credentials)


sh = gc.open_by_url("") #sheet url here
wks = sh.worksheet("Sheet1") #replace with sheet tab name here


cell_name_list = wks.range('A2:A100') #init enough lists to fill the sheet later
cell_family_list = wks.range('B2:B100')
cell_character_list = wks.range('C2:C100')
cell_lvl_list = wks.range('D2:D100')
cell_class_list = wks.range('E2:E100')
cell_ap_list = wks.range('F2:F100')
cell_awaap_list = wks.range('G2:G100')
cell_dp_list = wks.range('H2:H100')
cell_gearpic_list = wks.range('I2:I100')

bdo_classes = ['warrior', 'valkyrie', 'valk', 'wizard', 'wiz', 'witch', 'ranger', 'sorceress', 'sorc', 'berserker', 'tamer', 'musa', 'maehwa', 'lahn', 'ninja', 'kunoichi', 'kuno', 'dk', 'DK', 'striker', 'mystic']
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

def find_and_update(message):
    gc.login()
    infos = GEARdict[message.author.id]
    name = message.author.display_name
    try:
        cell = wks.find(infos[0]) #find fam name in sheet
        print("user found in sheet")
        try: #write the lists to the sheet
            wks.update_cell(cell.row,cell.col-1,name)
            wks.update_cell(cell.row,cell.col,infos[0])
            wks.update_cell(cell.row,cell.col+1,infos[1])
            wks.update_cell(cell.row,cell.col+2,infos[2])
            wks.update_cell(cell.row,cell.col+3,infos[3])
            wks.update_cell(cell.row,cell.col+4,infos[4])
            wks.update_cell(cell.row,cell.col+5,infos[5])
            wks.update_cell(cell.row,cell.col+6,infos[6])
            wks.update_cell(cell.row,cell.col+7,infos[7])
        except:
            print("failed to update sheet")
    except:
        next_row = next_available_row(wks)
        try: #write the lists to the sheet
            wks.update_cell(next_row,1,name)
            wks.update_cell(next_row,2,infos[0])
            wks.update_cell(next_row,3,infos[1])
            wks.update_cell(next_row,4,infos[2])
            wks.update_cell(next_row,5,infos[3])
            wks.update_cell(next_row,6,infos[4])
            wks.update_cell(next_row,7,infos[5])
            wks.update_cell(next_row,8,infos[6])
            wks.update_cell(next_row,9,infos[7])
        except:
            print("add new user to sheet fail")


async def send_timed_msg(message,embed,timer):
    await client.wait_until_ready()
    msg = await client.send_message(message.channel,embed=embed )
    await asyncio.sleep(timer) 
    await client.delete_message(msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    read_gear_list()

@client.event
async def on_message(message):
    if message.content.startswith('!gear'):
        if message.channel.id == '': #change channel id here
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
                                find_and_update(message)
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
                                find_and_update(message)
                                write_gear_list()
                                await client.send_message(message.channel,
                                                  "Your gear has been added ")
                    else:
                        await client.send_message(message.channel,
                                                  "Use a direct link to the picture (url must end with.png/.jpg) use ShareX it's free")
                else:
                    await client.send_message(message.channel, "Use !help")
            else:
                if msg:
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
                            embed = discord.Embed()
                            embed.set_author(name=userID,icon_url=message.mentions[0].avatar_url)
                            embed.set_thumbnail(url=message.mentions[0].avatar_url)
                            embed.add_field(name=message.mentions[0].display_name,value=classgs,inline=False)
                            embed.set_image(url=picurl)
                            #await send_timed_msg(message,embed,15) #timed message example
                            await client.send_message(message.channel,embed=embed)
                            break
                    else:
                       await client.send_message(message.channel,"Gear not found!")
                else:
                    await client.send_message(message.channel, "Use !gear + @someone!")

    elif message.content.startswith('!remove'):
        eval = await is_officer(message)
        if eval:
            if not message.mentions:
                id = format_input("!remove", message.content)
                for key in GEARdict:
                    if key == id:
                        list = GEARdict[key]
                        name = list[0]
                        delete_from_sheet(name)
                        del GEARdict[key]
                        write_gear_list()
                        await client.send_message(message.channel, "Gear has been removed")
                        break
                else:
                    await client.send_message(message.channel, "Gear not found!")
            else:    
                id = message.mentions[0].id
                for key in GEARdict:
                    if key == id:
                        list = GEARdict[key]
                        name = list[0]
                        delete_from_sheet(name)
                        del GEARdict[key]
                        write_gear_list()
                        await client.send_message(message.channel, "Gear has been removed")
                        break
                else:
                    await client.send_message(message.channel, "Gear not found!")
        else:
            await client.send_message(message.channel,
                                      "You ain't a maid!")


    elif message.content.startswith('!sheet'):  
        eval = await is_officer(message)
        if eval:
            i = 0
            gc.login() #refresh auth token
            for key in GEARdict.fromkeys(GEARdict): #parse tru every key in the map and convert the id to real username then append it to the cell lists
                user = await client.get_user_info(key)
                new_key = user.name
                cell_name_list[i].value = new_key
                infos = GEARdict[key]
                bdoclass = class_check(infos[3])
                cell_family_list[i].value = infos[0]
                cell_character_list[i].value = infos[1]
                cell_lvl_list[i].value = infos[2]
                cell_class_list[i].value = bdoclass
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
                i += 1
            else:
                await client.send_message(message.channel, "Number of users that submitted their gear: " + str(i))
        else:  
            await client.send_message(message.channel,
                                      "You ain't a maid!")

    elif message.content.startswith('!help'): 
        embed = discord.Embed()
        embed.set_author(name="Gear Help",icon_url=client.user.avatar_url)
        embed.set_thumbnail(url=client.user.avatar_url)
        embed.add_field(name="How To Add/Update Gear",value="!gear Family(name) Character(name) Level Class AP AWAAP DP Gear pic",inline=False)
        embed.add_field(name="Classes",value="For Dark Knight use dk",inline=False)
        embed.add_field(name="Gear pic rules",value="Use a direct link to the picture(url must end with .jpg/.png)use ShareX, it's free",inline=False)
        await client.send_message(message.channel,embed=embed)

client.run('')#add your bot token here
