#!/usr/env/bin python3
# Valley Discord Chat Bot
__version__ = "0.1.5"

import os
import sys
import traceback

import json

try:
    import __init__
    from __init__ import *
except:
    traceback.print_exc()
    sys.exit()
try:
    from Cogs.report import Report
    from Cogs.boards import Board
    from Cogs.temperature import Temperature
    from Cogs.admin import Admin
    from Cogs.logs import Logs
except:
    print("a cog is missing or corrupt, download a new version to "
        + "enable full functionality.")
    traceback.print_exc()
    sys.exit()


# command helpers
@bot.event
async def on_command_error(ctx, error):
    await handle_errors(ctx, error)


# message/command handler
@bot.event
async def on_message(message):
    await add_message(message)
    if message.author == bot.user:
        return
    mess = message.content.lower()
    if "http" in mess and not check_whitelist(message):
        await can_post(message)
    if message.author.guild_permissions.manage_messages:
        if mess.startswith("!mute"):
            await bot._BotBase__cogs['Admin']._mute(message)
        elif mess.startswith("!warn"):
            await bot._BotBase__cogs['Admin']._warn(message)
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    delta = datetime.utcnow() - member.created_at
    if delta.days < bot.TIME:
        await member.add_roles(bot.roles["youngling"])
        log = "@here {} / {} age: {} adding role.".format(
            member.name, member.mention, delta.days)
        await bot.logs.send(log)
    chirpers = (exec_sql(SQL["IS_FROZEN"], (member.id,)).
        fetchone())
    if chirpers is not None:
        if chirpers[0] == 1:
            await member.add_roles(bot.roles["freeze"])
        else:
            await bot._BotBase__cogs['Admin'].restore_roles(member)

@bot.event
async def on_member_remove(member):
    """Save member roles on quitting server"""
    if bot.roles['freeze'] not in member.roles:
        await store_roles(member,0)



@commands.command(name="help")
@commands.has_permissions(manage_messages=True)
async def _custom_help(ctx, *args):
    help = '\n'.join([
    ("`gk! die` will shut down the bot, don't do that (full only)"),
    ("`gk! thaw <list of users>` will unfreeze the listed users"),
    ("`gk! freeze <list of users>` will freeze the listed users"),
    ("`gk! messagemin: <integer>` will set the minimum message count"
        + " to the value provided (full only)"),
    ("`gk! passport <list of users>` removes 'customs' role from "
        + "users, allowing access to rules"),
    ("`gk! customs <list of users>` removes chirper, and adds "
        + "customs role"),
    ("`gk! voters <number of weekly posts to vote> "
        + "<list of channels to run on>` will return a list of "
        + "usernames for people who posted more than X number of "
        + "messages per week in each channel"),
    ("`gk! day/week/month <list of channels>` will return a count "
        + "of messages and users for each channel"),
    ("`gk! cat day/week` will run the category you are in all at "
        + "once"),
    ("`gk! filter (week/day): <term>` will run on all categories "
        + "containing that term"),
    ("`gk! modlogs <user>` will print a count of warns and mutes "
        + "recived by a user in gatekeeper logs"),
    ("`gk! leaderboard <optional number of users, default 10>` will "
        + "print top users by messages posted"),
    ("`gk! mayoboard <optional number of users, default 10>` will "
        + "print top users by messages posted containing the word "
        + "mayo"),
    ("`gk! modscoreboard` will print the the top mods by punishments"
        + " provided"),
    ])
    await ctx.send(help)


@bot.event
async def on_ready(ready_msg="Logged in as {name} ({id})",
    send_message=False):
    """initialize bot settings and info"""
    try:            
        # Obtain discord.Role objects for each id specified in
        # settings. Stores the roles into bot.settings["roles"]
        # which is cleared when bot exits to allow for portability
        # and easier maintainability.

        
        bot.aiosession = aiohttp.ClientSession(loop=bot.loop)
        bot.guild = bot.get_guild(bot.settings["guild"])
        bot.roles = OrderedDict()
        bot.fun_roles = OrderedDict()
        for role_key, role_id in bot.settings["roles"].items():
            bot.roles[role_key] = bot.guild.get_role(role_id)
        for role_key, role_id in bot.settings["fun_roles"].items():
            bot.fun_roles[role_key] = bot.guild.get_role(role_id)
        print(ready_msg.format(name=bot.user, id=bot.user.id))
        bot.logs = bot.get_channel(bot.settings["logs"])
        bot.remove_command("help")
        bot.add_command(_custom_help)
        bot.add_cog(Report(bot, SQL))
        bot.add_cog(Board(bot, SQL))
        bot.add_cog(Temperature(bot))
        bot.add_cog(Admin(bot, SQL))
        bot.add_cog(Logs(bot, SQL))
    except:
        traceback.print_exc()


if __name__ == "__main__":
    #main(bot)
    try:
        start()
    except:
        traceback.print_exc()
        sys.exit()