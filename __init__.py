#!/usr/env/bin python3

__version__ = "0.2.0"

#stdlib imports
import aiohttp
import argparse
import asyncio
import json
import inspect
import os
import pickle
import random
import re
import sqlite3
import sys
import subprocess
import traceback

from collections import OrderedDict
from datetime import datetime, timedelta
from sqlite3 import connect, Error, IntegrityError

# discord imports
import discord
from discord import Client
from discord.ext import commands

# custom imports
try:
    from Bin.secrets import Secrets
    from Bin.setting_manager import Program_Settings
    from sql_constants import SQL_STRINGS as SQL
    from Bin.settings import Settings as stest
except:
    traceback.print_exc()
    sys.exit()


# SQL functions
def create_db_connection(db_file):
    """Creates a SQL connection to the db_file"""
    connection = None
    try:
        connection = connect(db_file, timeout=3)
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


async def store_roles(user, to_freeze):
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


# error handler
async def handle_errors(ctx, error):
    """Class to handle command errors"""
    ignore_exceptions = bot.settings.get("ignore_errors", False)
    if ignore_exceptions == False:
        print(error)
        return
    for exc in ignore_exceptions:
        if isinstance(error, exc):
            return
    print(error)
    if ctx.bot.verbose == True:
        traceback.print_exc()
    return

# command line argument handler
def _args(description="Gatekeeper command line arguments"):
    """Parse command line arguments"""
    usage = "gatekeeper.py "
    parser = argparse.ArgumentParser(description=description, usage=usage)
    parser.add_argument('-t', '--test_mode', action='store_true')
    parser.add_argument('-r', '--reset', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    return args

# bot initialization
bot = commands.Bot(command_prefix=("gk! ", "gk!"), 
    case_insensitive=True, description="A bot for basic commands",
    self_bot=False, help_command=None)


def start(secret_file=r".\secret"):
    """
        starts the program by loading secrets file and setting things
        into motion
    """
    # setup and extract command line arguments
    cli_args = _args()
    test_mode = cli_args.test_mode
    reset = cli_args.reset
    verbosity = cli_args.verbose

    #sttng = stest(test_mode=test_mode, reset=reset)
    with open("init.json", "r") as fd:
        sttng = stest(json.load(fd))
    sttng.setattr(test_mode=test_mode, reset=reset, 
        verbose=verbosity)

    '''for key,val in vars(sttng).items():
        print(f"{key} = {val}")
        
    print(sttng.test_mode)
    print(sttng.reset)
    print(sttng.verbose)'''

    # setup settings and check settings_integrity
    settings_manager = Program_Settings(
        reset=reset, test_mode=test_mode)
    settings_manager.settings_integrity()
    settings = settings_manager.settings

    # setup and process secret
    secrets = Secrets(settings["secret_file"])
    bot.TIME = secrets.secret["time"]
    bot.verbose = verbosity
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
    print("bot exited")