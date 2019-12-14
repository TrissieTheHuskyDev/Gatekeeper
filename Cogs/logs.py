#!/user/bin/python3

# cog to log messages and react to various events

from discord.ext import commands
import discord
from pprint import pprint

from __init__ import handle_errors

class Logs(commands.Cog):

    def __init__(self, bot, sql):
        self.bot = bot
        self.sql = sql

    async def cog_check(self, ctx):
        return ctx.channel.has_permissions(ctx.author
            ).manage_channels
    
    async def on_command_error(self, ctx, error):
        await handle_errors(ctx, error)

    async def new_image_perms(self, before, after):
        new_roles = [role.name for role in 
            set(after.roles)-set(before.roles)]
        if "chirper2" in new_roles:
            await self.bot.logs.send(f"{before.mention} can now post images")
            

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await(self.new_image_perms(before, after))
