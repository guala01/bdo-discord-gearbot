import pickle
import json
import discord
from collections import defaultdict
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import validators

client = discord.Client()

GEARdict = defaultdict(list)

bdo_classes = ['warrior', 'valkyrie', 'wizard', 'witch', 'ranger', 'sorceress', 'berserker', 'tamer', 'musa', 'maehwa', 'lahn', 'ninja', 'kunoichi', 'dk', 'striker', 'mystic']
#missing check on eof and IOE
def write_gear_list():
    global GEARdict
    with open('gearlist', 'wb') as fp:
        pickle.dump(GEARdict, fp)
def read_gear_list():
    global GEARdict
    with open('gearlist', 'rb') as fp:
        GEARdict = pickle.load(fp)

#todo add custom roles or role by id
async def is_officer(message): 
    if "maids" in [y.name.lower() for y in message.author.roles]: #add your officier role name here
        return True

    return False

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('auth.json', scope)#add your json auth file name here and in the same folder

gc = gspread.authorize(credentials)

wks = gc.open("sheetname").sheet1 #add your sheet name here

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

#return the content of the msg so famn name + reason for absence
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
    read_gear_list() #this will fail if gearlist file is empty of not there at all


@client.event
async def on_message(message):
    if message.content.startswith('!gear'):
        msg = format_input("!gear", message.content) #cleanup the message
        if message.mentions == []: #if there's no mentions it means you want to add/update gears otherwise pull the mentioned gear out
            msg_list = msg.split(" ",3) #plit the msg in the first 3 arguments and check them one by one, futher args will be invalid, 
            if(len(msg_list) == 3 and msg_list[0].lower() in bdo_classes and msg_list[1].isnumeric() and validators.url(msg_list[2])):
                if msg: #will have an excpetion if one of the args is not present fix soon
                    if message.author.id in GEARdict.keys(): #if key is already there update it
                        del GEARdict[message.author.id]
                        GEARdict[message.author.id].append(msg_list[0])
                        GEARdict[message.author.id].append(msg_list[1])
                        GEARdict[message.author.id].append(msg_list[2])
                        write_gear_list()
                        await client.send_message(message.channel,
                                              "Your gear has been updated!")
                    else: #else add it anew
                        GEARdict[message.author.id].append(msg_list[0])
                        GEARdict[message.author.id].append(msg_list[1])
                        GEARdict[message.author.id].append(msg_list[2])
                        write_gear_list()
                        await client.send_message(message.channel,
                                          "Your gear has been added ")
            else:
                await client.send_message(message.channel, "Use !gear + class + GS + gear pic img (For Dark Knight use dk)")
        else:
            if msg:
                id = message.mentions[0].id
                for key in GEARdict:
                    if key == id:
                        userID = await client.get_user_info(key)
                        url = GEARdict[key]
                        picurl = url[2].strip()
                        stringfix = url[0] + " "+ url[1] #do some hacky shit to get the correct string and print in a nice embed
                        classgs = stringfix.strip()
                        embed = discord.Embed()
                        embed.set_author(name=userID,icon_url=message.mentions[0].avatar_url)
                        embed.set_thumbnail(url=message.mentions[0].avatar_url)
                        embed.add_field(name=message.mentions[0].display_name,value=classgs,inline=False)
                        embed.set_image(url=picurl)
                        await client.send_message(message.channel,embed=embed)
                        break;
                else:
                   await client.send_message(message.channel,"Gear not found!")
            else:
                await client.send_message(message.channel, "Use !gear + @someone you baka!")

    elif message.content.startswith('!remove'):
        eval = await is_officer(message)
        if eval:
            id = message.mentions[0].id
            for key in GEARdict:
                if key == id:
                    del GEARdict[key]
                    write_gear_list()
                    await client.send_message(message.channel, "Gear has been removed")
                    print("gear removed")
                    break;
            else:
                await client.send_message(message.channel, "Gear not found!")
        else:  
            await client.send_message(message.channel,
                                      "You ain't a maid you bitch")



    elif message.content.startswith('!sheet'): #this is very hacky but it works 
        eval = await is_officer(message)
        if eval:
            i = 0
            gc.login() #refresh auth token
            cell_name_list = wks.range('A2:A70') #init enough lists to fill the sheet later
            cell_class_list = wks.range('B2:B70')
            cell_gs_list = wks.range('C2:C70')
            cell_gearpic_list = wks.range('D2:D70')
            for key in GEARdict.fromkeys(GEARdict): #parse tru every key in the map and convert the id to real username then append it to the cell lists
                user = await client.get_user_info(key)
                new_key = user.name
                cell_name_list[i].value = new_key
                infos = GEARdict[key]
                cell_class_list[i].value = infos[0]
                cell_gs_list[i].value = infos[1]
                cell_gearpic_list[i].value = infos[2]
                i += 1
            try: #write the lists to the sheet
                wks.update_cells(cell_name_list)
                wks.update_cells(cell_class_list)
                wks.update_cells(cell_gs_list)
                wks.update_cells(cell_gearpic_list)
                await client.send_message(message.channel, "Gear updated on the sheet!")
            except:
                await client.send_message(message.channel, "API Error cause google is a giant cunt") #I don't like google api
        else:  
            await client.send_message(message.channel,
                                      "You ain't a maid you bitch")
	elif message.content.startswith('!check'): #self explanatory just counts how many entries we have got so far
        eval = await is_officer(message)
        if eval:
            i = 0
            for key in GEARdict.fromkeys(GEARdict):
                user = await client.get_user_info(key)
                i += 1
            else:
                await client.send_message(message.channel, "Number of cunts that submitted their gear: " + i)
        else:  
            await client.send_message(message.channel,
                                      "You ain't a maid you bitch")


client.run('')#add your bot token here
