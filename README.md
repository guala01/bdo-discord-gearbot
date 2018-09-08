# bdo-discord-gearbot
Very simple bot that will handle your guild gear and update it on a google spreasheet file to keep track of guild avg gs.
Bot will works with simple !gear command and has remove and sheet update features. It's not the cleanest code but does it's job and embeds are nice.

To run it you have to obtain google api auth file + unlock sheet and drive api. pip install discord, gspread, oauth2client, PyOpenSSL and validators (check gspread docs to install those 3).

To run it comment out read_gearlist on bot starup and submit a gear then remove the comment and it will run with no issues, have yet to fix it.
