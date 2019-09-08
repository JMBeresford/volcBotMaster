import json
import os
import platform

os_type = platform.system()
config = {}

try:
    term_size = os.get_terminal_size
except:
    pass
else:
    term_size = (0,0)

clear = "clear" if os_type == "Linux" else "cls"

header = '----------volcBotMaster Configuration----------\n\n'

os.system(clear)
print(header)

print("Welcome to the volcBotMaster configuration script\n\n")

config['prefix'] = input("Enter your desired command prefix (!, ?, !!, -, etc): ")

os.system(clear)

print(header)

config['owner_id'] = int(input( "Enter the ID of the bot owner (this can be found by right clicking"
                                " on your username in discord, assuming dev mode is on): "))

os.system(clear)
print(header)

config['mod_role'] = input( "Enter what you want your moderator role to be (leave blank for default,"
                            "'BotMechanic'): ")
if config['mod_role'] == '':
    config['mod_role'] = 'BotMechanic'

os.system(clear)
print(header)

config['admin_role'] = input(   "Enter what you want your admin role to be (leave blank for default"
                                ", 'BotOfficer'): ")
if config['admin_role'] == '':
    config['admin_role'] = 'BotOfficer'

os.system(clear)
print(header)

config['token'] = input("Enter your bot token: ")

os.system(clear)
print(header)

with open('config.json', 'w+') as file:
    json.dump(config, file)

print("Configuration complete, you may now run the bot.")