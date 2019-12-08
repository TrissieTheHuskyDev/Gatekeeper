#!/usr/env/bin python3

#stdlib imports
import argparse
import asyncio
from collections import OrderedDict
from datetime import datetime, timedelta
import inspect
import logging
import os
import pickle
import random
import re
import sqlite3
from sqlite3 import Error, IntegrityError
import sys
import traceback


# discord.py imports
import discord

from discord import Client
from discord.ext import commands



# custom imports
try:
    from setting_manager import *
except:
    print("settings_manage is missing or corrupt, please download "
        + "a new version")
    sys.exit()
try:
    from sql_constants import SQL_STRINGS as SQL
except:
    print("sql_constants.py is missing or corrupt, please download "
        +"a new version")
    sys.exit()


# SQL functions
def create_db_connection(db_file):
    """Creates a SQL connection to the db_file"""
    connection = None
    try:
        connection = sqlite3.connect(db_file, timeout=3)
        return connection
    except Error as err:
        print("Error establishing connection to the database\n"
                + "{err}".format(err=err))
    return connection


def create_table(conn, create_table_sql):
    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
    except Error as err:
        print("Error creating table {err}\nTable Details {table}".
            format(err=err, table=create_table_sql))


# discord.Role functions
def is_role_set(user_roles, role):
    """return True if role is in user_roles 
        return False otherwise"""
    if role in user_roles:
        return 1
    else:
        return 0


def store_roles(user, to_freeze):
    """create or replace SQL entry with roles for user"""
    role_store = OrderedDict()
    role_store["id"] = user.id
    user_roles = [role.name for role in user.roles]
    for key in bot.settings["roles"].keys():
        role_store[key] = is_role_set(user_roles, key)
    role_store["freeze"] = to_freeze
    exec_sql(SQL["STORE_ROLE"], list(role_store.values()))
    return role_store


async def remove_roles(user, roles):
    for role in roles:
        await user.remove_roles(bot.roles[role])


async def add_roles(user, roles):
    for role in roles:
        await user.add_roles(bot.roles[role])


async def manage_roles(user, roles):
    await add_roles(user,roles[0])
    await remove_roles(user,roles[1])
    
async def temp_decay(user, role):
    await user.add_roles(role)
    await asyncio.sleep(bot.settings["temp_decay"])
    await user.remove_roles(role)
    
# misc helpers
async def can_post(message):
    """check if user can post links based on numbed of posts made"""
    n_msg = exec_sql(SQL["MIN_MESSAGES"], (message.author.id,)
        ).fetchone()[0]
    if n_msg < bot.settings["num_messages"]:
        await manage_roles(message.author,(("freeze",),("chirper",)))
        msg = "@here Freezing user: {} Message Count: {}".format(
            message.author.mention, n_msg)
        await bot.logs.send(msg)
        embd = discord.Embed(title=message.channel.name, color=0x00ff00)
        embd.add_field(name="Content", value=message.content, inline=False)
        await bot.logs.send(embed=embd)
        await message.delete()
        

def check_whitelist(message):
    """check message against site whitelist"""
    mess = message.content.lower()
    for site in bot.settings["whitelist"]:
        if site in mess:
            return True
    return False


async def add_message(message):
    """log a message to the SQL db"""
    message_values = (
        message.id, message.author.id, message.channel.id,
        message.channel.name, message.guild.id, 
        message.clean_content, message.created_at
    )
    try:
        exec_sql(SQL["ADD_MESSAGE"], message_values)
    except IntegrityError:
        pass


def get_users(message, *args):
    """returns a list of discord.User objects from a series 
        of id's"""
    users = []
    for user_id in map(int, re.findall(r"[\d]{10,20}", 
        ' '.join(args))):
        user = bot.guild.get_member(user_id)
        if user is not None:
            users.append(user)
    return users


def exec_sql(sql_string, values):
    """runs a sql command and returns result"""

    cur = bot.conn.cursor()
    cur.execute(sql_string, values)

    if "INSERT" in sql_string:
        bot.conn.commit()
        return cur.lastrowid
    else:
        return cur


def exit_bot():
    """Helper to exit bot and then exit system"""
    '''loop = asyncio.get_event_loop()
    loop.create_task(bot.http.close())
    loop.create_task(bot.logout())'''
    
    os.system(r".\bin\kill.bat {}".format(os.getpid()))


def restart_bot():
    """restarts bot"""
    print("\n\n")
    frame = inspect.stack()[1].frame
    file_name = frame.f_code.co_filename
    os.system(r".\bin\restart.bat "
        +"{} {} {}".format(os.getpid(), sys.executable, file_name))


# bot initialization
bot = commands.Bot(command_prefix=("gk!", "!"), case_insensitive=True,
    description="A bot for basic commands", self_bot=False,
    help_command=None)


# command line argument handler
def _args(description="Gatekeeper command line arguments"):
    """Parse command line arguments"""
    usage = "gatekeeper.py "
    parser = argparse.ArgumentParser(description=description, usage=usage)
    parser.add_argument('-t', '--test_mode', action='store_true')
    parser.add_argument('-r', '--reset', action='store_true')
    args = parser.parse_args()
    return args


def start(secret_file=r".\secret"):
    """
        starts the program by loading secrets file and setting things
        into motion
    """
    # setup and extract command line arguments
    cli_args = _args()
    test_mode = cli_args.test_mode
    reset = cli_args.reset
    
    
    # setup settings and check settings_integrity
    
    settings_manager = Program_Settings(reset=reset, test_mode=test_mode)
    settings_manager.settings_integrity(test_mode=test_mode)
    settings = settings_manager.settings
    
    # setup and process secret
    secrets = Secrets(settings["secret_file"])
    TOKEN = secrets.secret["token"]
    
    # setup sql database and make sure that required tables are added
    conn = create_db_connection(settings["db_file"])
    if conn is not None:
        create_table(conn, SQL["CREATE_MESSAGE_TABLE"])
        create_table(conn, SQL["CREATE_ROLES_TABLE"])
        create_table(conn, SQL["CREATE_MODLOG_TABLE"])
    else:
        try:
            raise Exception("No connection to Database")
        except Exception as exc:
            traceback.print_exc()
    
    # setup local bot memory
    bot.conn = conn
    bot.settings = settings["bot_settings"]
    bot.settings_manager = settings_manager
    
    # start bot
    print("Logging in...")
    bot.run(TOKEN)
    