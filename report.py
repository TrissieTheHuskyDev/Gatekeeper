#!/usr/env/bin python3

# report.py is a cog from discord.ext.commands.cog

from discord.ext import commands
import discord
import re
import sqlite3
from sqlite3 import Error
from __init__ import bot, exec_sql
from sql_constants import SQL_STRINGS

REPORT_SQL = SQL_STRINGS["REPORTS"]
async def form_message(sql_key, ch=""):
    sql_list = REPORT_SQL[sql_key]
    if ch:
        num_messages = exec_sql(sql_list[0], (ch.id,)).fetchone()[0]
        num_users = exec_sql(sql_list[1], (ch.id,)).fetchone()[0]
    else:
        num_messages = exec_sql(sql_list[0], ()).fetchone()[0]
        num_users = exec_sql(sql_list[1], ()).fetchone()[0]
    try:
        return [ch.name, num_messages, num_users]
    except:
        return [num_messages, num_users]


async def multi_channel_prep(ctx, sql_prefix, *args, ch_list=False):
    ctx.channels = []
    timeframe = await get_sql_timeframe(ctx, args)
    if not timeframe and not ch_list:
        return
    if ch_list:
        sql_key = sql_prefix
        for ch in ctx.cat:
            ctx.channels.append(await form_message(sql_key, ch))
    else:
        sql_key = sql_prefix+timeframe
        for ch in ctx.cat.channels:
            ctx.channels.append(await form_message(sql_key, ch))
    ctx.channels.sort(key=lambda lst: lst[1], reverse=True)
    await multi_print(ctx, *args)
    return


async def multi_print(ctx, *args):
    for ch in ctx.channels:
        msg = "\n{}: Messages: {} Users: {}".format(
            ch[0],ch[1],ch[2])
        await ctx.send(msg)


async def none_found(ctx, *args):
    await ctx.send("Nothing found with search: {}".format(' '.join(args)))
    return


class join_args:
    result = ""
    def __init__(self, args):
        print(args)
        self.result = ' '.join(args)
        


async def get_sql_timeframe(ctx, *args):
    args = join_args(*args).result
    if "day" in args:
        return "DAY"
    elif "week" in args:
        return "WEEK"
    elif "month" in args:
        return "MONTH"
    else:
        return False
    

@bot.command()
async def filter(ctx, *args):
    ctx.found = False
    for category in bot.guild.categories:
        if category.name.lower() in ' '.join(args):
            ctx.cat = category
            await multi_channel_prep(ctx, "FILTER", *args)
            ctx.found = True
    if not ctx.found:
        await none_found(ctx, *args)
        return
    


@bot.command()
async def all(ctx, *args):
    sql_key = "ALL"
    timeframe = await get_sql_timeframe(ctx, args)
    if timeframe:
        vals = await form_message(sql_key+timeframe, ())
        msg ="\nAll Channels; Messages: {} Users: {}".format(*vals)
        await ctx.send(msg)
    else:
        ctx.cat = ctx.message.channel_mentions
        await multi_channel_prep(ctx, "ALL", *args, ch_list=True)

    
@bot.command()
async def cat(ctx, *args):
    ctx.cat = ctx.channel.category
    await multi_channel_prep(ctx, "CAT", *args)


@bot.command()
async def day(ctx, *args):
    ctx.cat = ctx.message.channel_mentions
    await multi_channel_prep(ctx, "DAY", *args, ch_list=True)


@bot.command()
async def week(ctx, *args):
    ctx.cat = ctx.message.channel_mentions
    await multi_channel_prep(ctx, "WEEK", *args, ch_list=True)


@bot.command()
async def month(ctx, *args):
    ctx.cat = ctx.message.channel_mentions
    await multi_channel_prep(ctx, "MONTH", *args, ch_list=True)