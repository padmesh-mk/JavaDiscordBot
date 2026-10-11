import discord
from discord.ext import commands

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Shows the bot's uptime."""
        # Calculate uptime
        now = discord.utils.utcnow()
        delta = now - self.bot.start_time

        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Format uptime message
        uptime_message = f"{days}d {hours}h {minutes}m {seconds}s"

        # Create embed
        embed = discord.Embed(
            title="Bot Uptime",
            description=f"The bot has been online for: **{uptime_message}**",
            color=0x00ffe5
        )
        embed.set_footer(
            text="Uptime info",
            icon_url="https://cdn.discordapp.com/icons/1063458575667699832/a_00030a2bbe60e06071ad5b259360ea53.gif?size=1024&width=640&height=640"
        )
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Uptime(bot))
