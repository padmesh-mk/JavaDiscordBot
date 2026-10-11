import discord
from discord.ext import commands

class Kik(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kik')
    async def kik(self, ctx, member: discord.Member = None, *, reason: str = 'no reason'):
        """Kick a user with a default reason (mock command)."""
        allowed_roles = ['1335128922446237696', '1313556608474812527', '1313596462621265932', '1206626888811020368', '1214099642908934155']
        
        # Check permission by role ID or role Name
        has_permission = any(str(role.id) in allowed_roles or role.name in allowed_roles for role in ctx.author.roles)
        
        if not has_permission:
            return await ctx.send('You do not have permission to use this command.')

        # If no member is mentioned, default to the command author
        target_member = member if member else ctx.author

        # Delete the original command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        # Send the mock kick message
        await ctx.send(f'Kicked **{target_member}** Reason: {reason}')

async def setup(bot):
    await bot.add_cog(Kik(bot))
