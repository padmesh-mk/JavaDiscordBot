import discord
from discord.ext import commands

class StaffRumble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='bat')
    async def bat(self, ctx, *, extra_text: str = None):
        """Ping for staff battles (staff battles member only)."""
        allowed_role_id = 1315719570396414144
        battle_role_mention = '<@&1313012309312012390>'

        if not ctx.guild:
            return await ctx.reply('This command can only be used in a server.')

        # Check if author has the allowed role
        has_role = any(role.id == allowed_role_id for role in ctx.author.roles)
        if not has_role:
            return await ctx.reply('You do not have permission to use this command!')

        try:
            # Delete command if possible
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass

            message_content = f"{battle_role_mention}\n\n{extra_text}" if extra_text else battle_role_mention
            await ctx.send(message_content)
        except Exception as e:
            await ctx.send(f"There was an error: `{str(e)}`")

async def setup(bot):
    await bot.add_cog(StaffRumble(bot))
