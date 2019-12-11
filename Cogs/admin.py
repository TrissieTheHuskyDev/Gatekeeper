import aiohttp
import inspect
import os
import csv
import io

from sqlite3 import IntegrityError
from traceback import print_exc

from discord.ext import commands
import discord

from __init__ import (exec_sql, handle_errors, re, get_users, 
    store_roles, remove_roles, sys)


class Admin(commands.Cog):

    def __init__(self, bot, sql, aiosession):
        self.bot = bot
        self.sql = sql
        self.execute = exec_sql
        self.aiosession = aiosession

    async def cog_check(self, ctx):
        return ctx.channel.permissions_for(ctx.author
            ).manage_messages

    async def cog_command_error(self, ctx, error):
        await handle_errors(ctx, error)

    async def exit_bot(self):
        """Helper to exit bot and then exit system"""
        try:
            await self.aiosession.close()
        except:
            pass
        await self.bot.logout()
        sys.exit()


    async def restart_bot(self):
        """restarts bot"""
        frame = inspect.stack()[1].frame
        file_name = frame.f_code.co_filename # get name of main file
        try:
            await self.aiosession.close()
        except:
            pass
        # await self.bot.logout()
        os.execl(sys.executable, sys.executable, * sys.argv)

    # commands available to full mods
    @commands.command(name="die")
    @commands.has_permissions(manage_channels=True)
    async def _die(self, ctx):
        await ctx.send("Quitting")
        await self.exit_bot()

    @commands.command(name="restart")
    @commands.has_permissions(manage_channels=True)
    async def _restart(self, ctx):
        await ctx.send("Restarting")
        try:
            await self.restart_bot()
        except:
            print_exc()
            sys.exit()

    @commands.command(name="messagemin")
    @commands.has_permissions(manage_channels=True)
    async def _message_min(self, ctx, m_min):
        try:
            self.bot.settings["num_messages"] = int(m_min)
            self.bot.settings_manager.set_settings(self.bot.settings)
            
            msg = f"Minimum message count for linking set to: {m_min}."
        except ValueError:
            msg = (f"Invalid Integer entered for messagemin command: {m_min}")
        await self.bot.logs.send(msg)

    # Commands available to trial mods and up
    @commands.command(name="warn")
    async def _warn(self, ctx, *, args:str):
        users = get_users(ctx.message, args)
        message = ctx.message
        for index, user in enumerate(users):
            try:
                mod_log = (
                    message.id+index, message.author.id, message.channel.id,
                    message.channel.name, message.guild.id, 
                    message.clean_content, message.created_at, user.id, 0
                    )
                last_row_id = self.execute(self.sql["ADD_MODLOG"], 
                    mod_log)
                mod_logs = self.execute(self.sql["MOD_LOGS"], (user.id,
                    )).fetchone()[1]
            except IntegrityError:
                mod_log = (
                    self.bot.last_row_id+index, message.author.id, message.channel.id,
                    message.channel.name, message.guild.id, 
                    message.clean_content, message.created_at, user.id, 0
                    )
                last_row_id = self.execute(self.sql["ADD_MODLOG"], mod_log)
            if mod_logs % 5 == 0:
                msg = f"{user.mention} has {mod_logs} modlog(s)"
                await self.bot.logs.send(msg)

    @commands.command(name="mute")
    async def _mute(self, ctx, *, args:str):
        users = get_users(ctx.message, args)
        message = ctx.message
        for index, user in enumerate(users):
            try:
                mod_log = (
                    message.id+index, message.author.id, message.channel.id,
                    message.channel.name, message.guild.id, 
                    message.clean_content, message.created_at, user.id, 1
                    )
                last_row_id = self.execute(self.sql["ADD_MODLOG"], 
                    mod_log)
                mod_logs = self.execute(self.sql["MOD_LOGS"], 
                    (user.id,)).fetchone()[1]
            except IntegrityError:
                mod_log = (
                    self.bot.last_row_id+index, message.author.id, message.channel.id,
                    message.channel.name, message.guild.id, 
                    message.clean_content, message.created_at, user.id, 1
                    )
                last_row_id = self.execute(self.sql["ADD_MODLOG"], mod_log)
            if mod_logs % 5 == 0:
                msg = f"{user.mention} has {mod_logs} modlog(s)"
                await self.bot.logs.send(msg)

    @commands.command(name="thaw")
    async def _thaw(self, ctx, *args):
        """Unfreezes a user"""
        users = get_users(ctx.message, *args)
        for user in users:
            await user.remove_roles(self.bot.roles["freeze"])
            chirpers = self.execute(self.sql["RETRIEVE_ROLE"], (user.id,)).fetchone()
            if chirpers is not None:
                for index, (key, chirper) in enumerate(self.bot.roles.items()):
                    if(index >= len(chirpers)):
                        break
                    if chirpers[index] == 1 and key.startswith("chirper"):
                        await user.add_roles(chirper)
            msg = f"Unfroze user: {user.mention}"
            user_roles = store_roles(user, 0)
            await ctx.send(msg)

    @commands.command(name="freeze")
    async def _freeze(self, ctx, *args):
        del_roles = ["chirper", "chirper2", "chirper3", "chirper4"]
        users = get_users(ctx.message, *args)
        for user in users:
            if(self.bot.roles["freeze"] in user.roles):
                msg = "{user_mention} is already frozen!".format(
                    user_mention=user.mention)
            else:
                await user.add_roles(self.bot.roles["freeze"])
                store_roles(user, 1)
                await remove_roles(user, del_roles)
                msg = f"Froze user: {user.mention}"
            await ctx.send(msg)

    @commands.command(name="customs")
    async def _customs(self, ctx, *args):
        roles = ["chirper","chirper2","chirper3","chirper4"]
        users = get_users(ctx.message, *args)
        pass
        for user in users:
            await user.add_roles(self.bot.roles["youngling"])
            await remove_roles(user, roles)
            msg = f"Removed access to rules/chirper for {user.mention}"
            await ctx.send(msg)

    @commands.command(name="passport")
    async def _passport(self, ctx, *args):
        users = get_users(ctx.message, *args)
        for user in users:
            await user.remove_roles(self.bot.roles["youngling"])
            msg = f"Granted access to rules for {user.mention}"
            await ctx.send(msg)

    @commands.command(name="voters")
    async def _voters(self, ctx, *args):
        voters = re.match('\d+', ' '.join(args))
        if voters is None:
            voters = self.bot.settings["voters"]
        else:
            voters = int(voters.group())
        for channel in ctx.message.channel_mentions:
            get_voters = [user[0] for user in # get user ids
                self.execute(self.sql["VOTERS"], 
                    (channel.id, voters)).fetchall()]
            # get user objects
            users = tuple(self.bot.guild.get_member(user_id) for
                user_id in get_voters)
            msg =  '\n'.join([f"Voters for {channel.name}"] 
                + [f"{user.name}#{user.discriminator}" for user 
                in users if user is not None and not user.bot])
            await ctx.send(msg)

    @commands.command(name="modlogs")
    async def _mod_logs(self, ctx, *args):
        users = get_users(ctx.message, *args)
        for user in users:
            log_count = self.execute(self.sql["MOD_LOGS"], 
                (user.id,)).fetchone()[1]
            msg = f"{user.mention} has {log_count} modlog(s)"
            await self.bot.logs.send(msg)

    @commands.command(name="inactiveroles")
    async def _inactive_roles(self, ctx, *args):
        roles = self.bot.guild.roles
        csv_data = '\n'.join(f"{role.name}, {len(role.members)}" for role in roles)
        mem_file_in = io.BytesIO(csv_data.encode(encoding='utf-8'))
        await ctx.send(file=discord.File(mem_file_in, filename='Inactive Roles.csv'))




