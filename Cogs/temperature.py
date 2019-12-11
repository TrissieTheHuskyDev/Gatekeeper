from discord.ext import commands
import discord
import random
from asyncio import create_task, sleep
from __init__ import exec_sql, handle_errors, get_users

class Temperature(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        await handle_errors(ctx, error)

    def can_warm(self, ctx):
        return ((self.bot.fun_roles["warm"] in ctx.message.author.roles or
            self.bot.fun_roles["burning"] in ctx.message.author.roles) or
            ctx.channel.permissions_for(ctx.author).manage_messages)

    def can_cool(self, ctx):
        return (self.bot.fun_roles["cold"] in ctx.message.author.roles or
            self.bot.fun_roles["permafrost"] in ctx.message.author.roles or
            ctx.channel.permissions_for(ctx.author).manage_messages)

    async def temp_decay(self, user, role):
        await user.add_roles(role)
        await sleep(self.bot.settings["temp_decay"])
        await user.remove_roles(role)

    async def _change_temperature(self, ctx, user, temperature):
        """warms/cools user(s) specified"""

        if self.bot.fun_roles["heatproof"] in user.roles:
            passed = False
            msg = "I can't {} {} they're wearing thermal undies.".format(
                temperature, user.mention,)
        else:
            passed = True
            msg = "Ok, {} {}".format(user.mention, random.choice(
                self.bot.settings[temperature+"_responses"]))
        await ctx.send(msg)
        return passed

    @commands.command(name="warm")
    async def _warm(self, ctx, *args):
        """warm a user and then add task to remove warm role"""
        if not self.can_warm(ctx):
            return
        users = get_users(ctx.message, *args)
        for user in users:
            if (self.bot.fun_roles["permafrost"] in user.roles):
                msg = "I can't warm {} they're permafrozen".format(
                    user.mention)
                await ctx.send(msg)
                return
            if not await self._change_temperature(ctx, user, "warm"):
                return
            # add role to user and start timer, remove role after timer
            #   expires.
            warmin = create_task(self.temp_decay(
                user, self.bot.fun_roles["warm"]))
                
    @commands.command(name="cool")
    async def _cool(self, ctx, *args):
        """cool a user and then add task to remove cool role"""
        if not self.can_cool(ctx):
            return
        users = get_users(ctx.message, *args)
        for user in users:
            if (self.bot.fun_roles["burning"] in user.roles):
                msg = "I can't cool {} they're burning".format(
                    user.mention)
                await ctx.send(msg)
                return
            if not await self._change_temperature(ctx, user, "cool"):
                return
            coolin = create_task(self.temp_decay(
                user, self.bot.fun_roles["cold"]))