#!/usr/env/bin python3

#stdlib imports
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

 
# misc helpers
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


def exit_bot(bot, restart=False):
    """Helper to exit bot and then exit system"""
    bot.clear()
    try:
        bot.loop.create_task(bot.logout())
        bot.loop.create_task(bot.http.close())
    except:
        pass
    if restart:
        return
    sys.exit()


def restart_bot(bot):
    """restarts bot"""
    print("\n\n")
    frame = inspect.stack()[1].frame
    file_name = frame.f_code.co_filename
    exit_bot(bot, restart=True)
    os.system("python {file}".format(file=file_name))




bot = commands.Bot(command_prefix=("gk!", "!"), case_insensitive=True,
    description="A bot for basic commands", self_bot=False,
    help_command=None)

def start(secret_file=r".\secret"):
    """
        starts the program by loading secrets file and setting things
        into motion
    """
    settings_manager = Program_Settings(reset=True, test_mode=True)
    settings = settings_manager.settings
    secrets = Secrets(settings["secret_file"])
    TOKEN = secrets.secret["token"]
    conn = create_db_connection(settings["db_file"])
    if conn is not None:
        create_table(conn, SQL["CREATE_MESSAGE_TABLE"])
        create_table(conn, SQL["CREATE_ROLES_TABLE"])
    else:
        try:
            raise Exception("No connection to Database")
        except Exception as exc:
            print(exc)
    bot.conn = conn
    bot.settings = settings["bot_settings"]
    bot.settings_manager = settings_manager
    TOKEN = 'NjUwNzM5MjM4NDQyMzY5MDQ4.XePuKQ.CUj92A-1mVsRxqZIKWCVCHkNt2c'
    
    bot.run(TOKEN)
    