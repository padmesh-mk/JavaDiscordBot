import discord
from discord.ext import commands

class Membercount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='membercount', aliases=['mc'])
    async def membercount(self, ctx):
        """Shows the current member count of the server, including bots and real members."""
        if not ctx.guild:
            return await ctx.send("This command can only be used in a server.")

        total_members = ctx.guild.member_count
        bots = sum(1 for member in ctx.guild.members if member.bot)
        real_members = total_members - bots

        embed = discord.Embed(
            title='📊 Guild Members',
            description=(
                f'There are **{total_members}** members in this guild.\n'
                f'🧑 Real Members: **{real_members}**\n🤖 Bots: **{bots}**'
            ),
            color=0x00ffe5
        )
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Membercount(bot))
