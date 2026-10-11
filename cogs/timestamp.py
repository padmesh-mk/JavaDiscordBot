import discord
from discord.ext import commands
from discord import app_commands
import re
import time as time_module

class Timestamp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name='timestamp',
        aliases=['ts'],
        description='Convert time like 1d2h3m into a Discord timestamp'
    )
    @app_commands.describe(time='Enter time like 1d2h3m or 30s')
    async def timestamp(self, ctx, *, time: str = None):
        """Convert time like 1d2h3m into a Discord timestamp."""
        if not time:
            return await ctx.send("❌ | Provide time like `1d2h3m` or `30s`.")

        time_regex = re.compile(r"(\d+)\s*d|(\d+)\s*h|(\d+)\s*m|(\d+)\s*s", re.IGNORECASE)
        days = hours = minutes = seconds = 0
        
        matches = list(time_regex.finditer(time))
        if not matches:
            return await ctx.send("❌ | Invalid time format.")

        for match in matches:
            if match.group(1):
                days = int(match.group(1))
            if match.group(2):
                hours = int(match.group(2))
            if match.group(3):
                minutes = int(match.group(3))
            if match.group(4):
                seconds = int(match.group(4))

        total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
        if total_seconds <= 0:
            return await ctx.send("❌ | Invalid time format.")

        now = int(time_module.time())
        end_timestamp = now + total_seconds

        await ctx.send(
            content=f"<t:{end_timestamp}:R>\n<t:{end_timestamp}:T>",
            allowed_mentions=discord.AllowedMentions.none()
        )

async def setup(bot):
    await bot.add_cog(Timestamp(bot))
