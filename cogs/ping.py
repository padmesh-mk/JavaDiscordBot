import discord
from discord.ext import commands
import time

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='ping', description='Checks the bot latency.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        """Checks the bot latency."""
        # Calculate latency
        if ctx.interaction:
            created_at = ctx.interaction.created_at
        else:
            created_at = ctx.message.created_at

        # Time difference in milliseconds
        latency = round((discord.utils.utcnow() - created_at).total_seconds() * 1000)
        api_latency = round(self.bot.latency * 1000)

        # Create an embed for the response
        embed = discord.Embed(
            title='🏓 Pong!',
            description=f"**Bot Latency:** {latency}ms\n**API Latency:** {api_latency}ms",
            color=0x00c0ff
        )
        embed.timestamp = discord.utils.utcnow()

        # Send response
        await ctx.send(embed=embed)

        # Optionally delete prefix command message
        if not ctx.interaction:
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(Ping(bot))
