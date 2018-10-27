# bdo-discord-gearbot
Very simple bot that will handle your guild gear and keep it updated on a google spreasheet file to keep track of guild members.
Bot will work with !gear command and has remove and sheet update features to keep track of everything. It's not the cleanest code but does it's job and embeds are nice.

To run it you have to obtain google api auth file + unlock sheet and drive api(check gspread docs for better infos). 
pip install discord, gspread, oauth2client, PyOpenSSL(those 3 are for spreadsheet access) and validators and don't forget to give sheet access to your mail in json api file(check gpsread doc for more info).

Bot has:

!gear + parameters (family name, char name, class, level, ap, awaap, dp, gear pict link) to submit your gear

!gear + @mention to see someone else gear

!sheet to export/update the gear on a new google spreadsheet (bot automatically updates the gear on the sheet for you, so this command is to use only if you want a full update for any reason or to update a new sheet)

!remove + @mention or Discord ID

!help to show commands/indications

Bot can be edited for other mmos/games just dm me on discord and will help you out.

Lolzy#3416 for questions, bug or suggestions.
