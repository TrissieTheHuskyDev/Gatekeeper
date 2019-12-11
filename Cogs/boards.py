from discord.ext import commands
import discord
from __init__ import exec_sql, handle_errors, re

class Board(commands.Cog):

    def __init__(self, bot, sql):
            self.bot = bot
            self.sql = sql
            self.execute = exec_sql

    async def cog_check(self, ctx):
        return ctx.channel.permissions_for(ctx.author
            ).manage_messages

    async def cog_command_error(self, ctx, error):
        await handle_errors(ctx, error)

    async def lead_brd(self, ctx, sql_key, board_header, count_str,
        *args, count=10):
        """function to print out different kinds of leaderboards"""
        sql_statement = self.sql[sql_key]
        if sql_statement.count('?') > 0:
            # get number of users to retrieve and display
            if len(args) == 0:
                count_results = "{} ".format(count)
            else:
                count_results = re.search("\d+", ''.join(*args))
                if count_results is not None:
                    count_results = "{} ".format(count_results.group())
                    count = int(count_results)
                else:
                    count_results = "{} ".format(count_results)
            # get result of sql qry when leader/mayo board is used
            sql_results = self.execute(sql_statement, 
                (self.bot.user.id, ctx.guild.id, count)
                ).fetchall()
        else:
            # get result of sql qry when modscoreboard is used
            count_results = ""
            sql_results = self.execute(sql_statement, ()).fetchall()
        row_no = 1 # keep track of position on board
        msg = "Top {}{}:\n".format(count_results, board_header)
        #display num. user#discriminator num of msg type of msg
        for row in sql_results:
            user = self.bot.get_user(row[0])
            if user is not None and not user.bot:
                msg += "{}. {}#{} : {} {}\n".format(
                    row_no, user.name, user.discriminator, row[1],
                    count_str)
                row_no += 1
        await ctx.send(msg)

    @commands.command(name="leaderboard")
    async def _leader_board(self, ctx, *args):
        await self.lead_brd(ctx, "LEADERBOARD", "posters", "Messages", *args)

    @commands.command(name="mayoboard")
    async def _mayo_board(self, ctx, *args):
        await self.lead_brd(ctx, "MAYOBOARD", "mayoers", "Mayos", *args)

    @commands.command(name="modscoreboard")
    async def _mod_score_board(self, ctx, *args):
        await self.lead_brd(ctx, "MOD_SCOREBOARD", "punishers",
            "Punishments", *args)