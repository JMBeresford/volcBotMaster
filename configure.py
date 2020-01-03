import json
import os
import platform
import psycopg2

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
print(  "This bot uses PostreSQL, please enter the relevant info for your instance.\n"
        "Note: You are expected to have the database server setup of your own accord.\n\n")

while True: # smirks in evil
    config['db_host'] = input("Enter the host for your Postgres Database: ")
    config['db_port'] = input("Enter the port for your Postgres Database: ")
    config['db_name'] = input("Enter the name of your Postgres database: ")
    config['db_user'] = input("Enter the user for your database instance: ")
    config['db_password'] = input(f"Enter the password for {config['db_user']}: ")

    try:
        conn = psycopg2.connect(user = config['db_user'],
                                password = config['db_password'],
                                host = config['db_host'],
                                port = config['db_port'],
                                dbname = config['db_name'])

        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS members(id BIGINT PRIMARY KEY, name VARCHAR(255), join_date TIMESTAMP, guilds BIGINT[]);")
        cur.execute('''CREATE TABLE IF NOT EXISTS messages( id BIGSERIAL PRIMARY KEY,
                                                            author_id BIGINT,
                                                            author_name VARCHAR(255),
                                                            sent_at TIMESTAMP,
                                                            guild_id BIGINT,
                                                            channel_id BIGINT,
                                                            content TEXT);''')

        conn.commit()

    except (Exception, psycopg2.Error) as error:
        print("There was an error with the given connection:\n", error)
        input("Press enter to retry\n\n")
        continue

    else:
        try:
            cur.close()
            conn.close()
            print("Database preparation complete.\n")
            break

        except:
            print("Database preparation complete.\n")
            pass

os.system(clear)
print(header)

with open('config.json', 'w+') as file:
    json.dump(config, file)

print("Configuration complete, you may now run the bot.")