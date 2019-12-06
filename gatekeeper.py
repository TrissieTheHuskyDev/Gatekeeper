# Valley Discord Chat Bot
# python3
# imports and helper functions contained within __init__

try:
    from __init__ import *
except:
    print("__init__.py is missing or corrupt, please download a new version")
    sys.exit
try:
    from report import *
except:
    print("report is missing or corrupt, download a new version to "
        + "enable report commands including leaderboard")
    traceback.print_exc()


# command helpers
async def lead_brd(ctx, sql_key, board_header, count_str, *args, 
    count=10, count_display=True):
    try:
        count = int(re.search("\d+", join_args(args).result).group())
    except:
        pass
    try:
        sql_results = exec_sql(SQL[sql_key], (
            bot.user.id, bot.guild.id, count)).fetchall()
    except:
        sql_results = exec_sql(SQL[sql_key], ()).fetchall()
    count = min(len(sql_results), count)
    row_no = 1
    if count_display:
        msg = "Top {} {}:\n".format(count, board_header)
    else:
        msg = "Top {}\n".format(board_header)
    for row in sql_results:
        user = bot.get_user(row[0])
        if user is not None and not user.bot:
            msg += "{}. {}#{} : {} {}\n".format(
                row_no, user.name, user.discriminator, row[1],
                count_str)
            row_no += 1
    await ctx.send(msg)


# message/command handler
@bot.event
async def on_message(message):
    if message.author != bot.user:
        try:
            if message.author.guild_permissions.manage_messages:
                try:
                    if message.content.lower().startswith("gk! "):
                        message.content = "gk!"+message.content[4:]
                except:
                    traceback.print_exc()
                    sys.exit()
                await bot.process_commands(message)
            else:
                return
        except AttributeError:
            return


# full admin only commands
@bot.command()
async def die(ctx):
    """will shut down the bot, don't do that (full only)"""
    if ctx.author.guild_permissions.manage_channels:
        await ctx.send("Quitting")
        exit_bot(bot)
    else:
        await ctx.send("You don't have access to this command")
    
    
@bot.command()
async def restart(ctx):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.send("Restarting")
        restart_bot(bot)
    else:
        await ctx.send("You don't have access to this command")
        
        
@bot.command()
async def messagemin(ctx, m_min):
    try:
        bot.settings["num_messages"] = int(m_min)
        bot.settings_manager.set_settings(bot.settings)
        msg = ("Minimum message count for linking set to: {m_min}.".
            format(m_min=m_min))
    except ValueError as exc:
        msg = ("Invalid Integer entered for messagemin command")
    await ctx.send(msg)
    

# trial admin+ commands
@bot.command()
async def warn(ctx, *, args:str):
    users = get_users(ctx.message, args)
    message = ctx.message
    for index, user in enumerate(users):
        try:
            mod_log = (
                message.id+index, message.author.id, message.channel.id,
                message.channel.name, message.guild.id, 
                message.clean_content, message.created_at, user.id, 0
                )
            last_row_id = exec_sql(SQL["ADD_MODLOG"], mod_log)
            mod_logs = exec_sql(SQL["MOD_LOGS"], (user.id,)).fetchone()[1]
        except IntegrityError:
            mod_log = (
                bot.last_row_id+index, message.author.id, message.channel.id,
                message.channel.name, message.guild.id, 
                message.clean_content, message.created_at, user.id, 0
                )
            last_row_id = exec_sql(SQL["ADD_MODLOG"], mod_log)
        if mod_logs % 5 == 0:
            msg = "{user} has {mod_logs} modlog(s)".format(
                user=user.mention, mod_logs=mod_logs)
            await ctx.send(msg)
            
            
@bot.command()
async def mute(ctx, *, args:str):
    users = get_users(ctx.message, args)
    message = ctx.message
    for index, user in enumerate(users):
        try:
            mod_log = (
                message.id+index, message.author.id, message.channel.id,
                message.channel.name, message.guild.id, 
                message.clean_content, message.created_at, user.id, 1
                )
            last_row_id = exec_sql(SQL["ADD_MODLOG"], mod_log)
            mod_logs = exec_sql(SQL["MOD_LOGS"], (user.id,)).fetchone()[1]
        except IntegrityError:
            mod_log = (
                bot.last_row_id+index, message.author.id, message.channel.id,
                message.channel.name, message.guild.id, 
                message.clean_content, message.created_at, user.id, 1
                )
            last_row_id = exec_sql(SQL["ADD_MODLOG"], mod_log)
        if mod_logs % 5 == 0:
            msg = "{user} has {mod_logs} modlog(s)".format(
                user=user.mention, mod_logs=mod_logs)
            await ctx.send(msg)
            
            
@bot.command()
async def thaw(ctx, *args):
    """Unfreezes a user"""
    users = get_users(ctx.message, *args)
    for user in users:
        await user.remove_roles(bot.roles["freeze"])
        chirpers = exec_sql(SQL["RETRIEVE_ROLE"], (user.id,)).fetchone()
        if chirpers is not None:
            for index, (key, chirper) in enumerate(bot.roles.items()):
                if(index >= len(chirpers)):
                    break
                if chirpers[index] == 1 and key.startswith("chirper"):
                    await user.add_roles(chirper)
        msg = "Unfroze user: {user_mention}".format(
            user_mention=user.mention)
        user_roles = store_roles(user, 0)
        await ctx.send(msg)
        
        
@bot.command()
async def freeze(ctx, *args):
    roles = ["chirper", "chirper2", "chirper3", "chirper4"]
    users = get_users(ctx.message, *args)
    for user in users:
        if(bot.roles["freeze"] in user.roles):
            msg = "{user_mention} is already frozen!".format(
                user_mention=user.mention)
        else:
            await user.add_roles(bot.roles["freeze"])
            store_roles(user, 1)
            await remove_roles(user, roles)
            msg = "Froze user: {user_mention}".format(
                user_mention=user.mention)
        await ctx.send(msg)

        
@bot.command()
async def customs(ctx, *args):
    roles = ["chirper","chirper2","chirper3","chirper4"]
    users = get_users(ctx.message, *args)
    pass
    for user in users:
        await user.add_roles(bot.roles["youngling"])
        await remove_roles(user, roles)
        msg = ("Removed access to rules/chirper for {user_mention}".
            format(user_mention=user.mention))
        await ctx.send(msg)


@bot.command()
async def passport(ctx, *args):
    users = get_users(ctx.message, *args)
    for user in users:
        await user.remove_roles(bot.roles["youngling"])
        msg = "Granted access to rules for {user_mention}".format(
            user_mention=user.mention)
        await ctx.send(msg)

@bot.command(name="voters")
async def _voters(ctx, *args):
    try:
        voters = int(re.search('[0-9]+', join_args(
            args).result).group())
    except:
        voters = 5
    for ch in ctx.message.channel_mentions:
        msg = ch.name + "\n"
        get_voters = exec_sql(SQL["VOTERS"], (ch.id, voters))
        for data in get_voters:
            voter = bot.get_user(data[0])
            if voter is not None and voter.bot == False:
                msg += voter.name + "#" + voter.discriminator + "\n"
        await ctx.send(msg)


@bot.command(name="leaderboard")
async def _leader_board(ctx, *args):
    await lead_brd(ctx, "LEADERBOARD", "posters", "Messages", *args)


@bot.command(name="mayoboard")
async def _mayo_board(ctx, *args):
    await lead_brd(ctx, "MAYOBOARD", "mayoers", "Mayos", *args)


@bot.command(name="modlogs")
async def _mod_logs(ctx, *args):
    users = get_users(ctx.message, *args)
    for user in users:
        log_count = exec_sql(
            SQL["MOD_LOGS"], (user.id,)).fetchone()[1]
        msg = "{} has {} modlog(s)".format(user.mention, log_count)
        await bot.logs.send(msg)
        

@bot.command(name="modscoreboard")
async def _mod_score_board(ctx, *args):
    await lead_brd(ctx, "MOD_SCOREBOARD", "punishers",
        "Punishments", *args, count_display=False)


@bot.command()
async def warm(ctx, *args):
    #implement later
    pass

@commands.command(name="help")
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
    except Exception as exc:
        traceback.print_exc()


# program initialization includes:
#   logger setup - logger for bot for easy logging of info and the 
#       ability to turn debugging on or off
#   main() - Loads settings, sets up database connection, and 
#       initializes bot connection
logger = logging.getLogger('information')
    


if __name__ == "__main__":
    #main(bot)
    try:
        start()
    except:
        sys.exit()

