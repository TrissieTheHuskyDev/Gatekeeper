from discord.ext import commands
import discord
from sql_constants import SQL_STRINGS
from __init__ import exec_sql, handle_errors

class reporting(commands.Cog):
    reports = []

    def __init__(self, bot, sql):
        self.bot = bot
        global SQL_STRINGS
        global exec_sql
        self.execute = exec_sql
        self.SQL = SQL_STRINGS

    async def cog_check(self, ctx):
        return ctx.channel.permissions_for(
            ctx.author).manage_messages

    async def cog_command_error(self, ctx, error):
        await handle_errors(ctx, error)
        
    def form_report(self, sql_key, channel=""):
        results = self.execute(self.SQL[sql_key], ((channel.id,)
            if channel else ())).fetchone()
        return ([channel.name, results[0], results[1]] 
            if channel else [results[0], results[1]])

    def get_sql(self, args):
        for time in ["day", "week", "month"]:
            if time in args:
                return time.upper()
        return ""

    async def submit_report(self, ctx):
        for report in self.reports:
            if len(report) == 2:
                await ctx.send("\n{}: Messages: {} Users: {}".format(
                    "All Channels", report[0], report[1]))
            else:
                await ctx.send("\n{}: Messages: {} Users: {}".format(
                    report[0], report[1], report[2]))
    
    async def report_prep(self, ctx, *args, sql_prefix=""):
        self.reports = []        
        arg_str = ' '.join(args)
        sql_key = sql_prefix+self.get_sql(arg_str)
        if len(ctx.ch_list) > 0:
            for channel in ctx.ch_list:
                self.reports.append(
                    self.form_report(sql_key, channel))
        else:
            try:
                print(sql_key)
                self.reports.append(
                    self.form_report(sql_key))
            except:
                pass
        await self.submit_report(ctx)
        self.reports = []
        return

    async def none_found(ctx, *args):
        await ctx.send("Nothing found with search: {}".format(
            ' '.join(args)))
        return

    @commands.command()
    async def filter(self, ctx, *args):
        ctx.ch_list = []
        arg_str = ' '.join(args)
        for category in self.bot.guild.categories:
            if category.name.lower() in arg_str:
                ctx.ch_list += category.channels
        if len(ctx.ch_list) == 0:
            await self.none_found(ctx, *args)
        else:
            await self.report_prep(ctx, *args)

    @commands.command()
    async def all(self, ctx, *args):
        if len(ctx.message.channel_mentions) >= 1:
            ctx.ch_list = ctx.message.channel_mentions
            await self.report_prep(ctx, *args, sql_prefix="ALL")
        else:
            ctx.ch_list = ""
            await self.report_prep(ctx, *args, sql_prefix="ALL")
            
    @commands.command()
    async def cat(self, ctx, *args):
        ctx.ch_list = ctx.channel.category.channels
        await self.report_prep(ctx, *args)

    @commands.command()
    async def week(self, ctx, *args):
        ctx.ch_list = ctx.message.channel_mentions
        await self.report_prep(ctx, *args, sql_prefix="WEEK")

    @commands.command()
    async def day(self, ctx, *args):
        ctx.ch_list = ctx.message.channel_mentions
        await self.report_prep(ctx, *args, sql_prefix="DAY")

    @commands.command()
    async def month(self, ctx, *args):
        ctx.ch_list = ctx.message.channel_mentions
        await self.report_prep(ctx, *args, sql_prefix="MONTH")