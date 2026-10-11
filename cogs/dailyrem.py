import discord
from discord.ext import commands

class Dailyrem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='rem')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rem(self, ctx):
        """Daily Reminder."""
        embed = discord.Embed(
            title='Daily Reminder',
            color=0x00c0ff,
            description=(
                '**Dank Memer:** \n'
                '- Daily: </daily:1011560370864930856> \n'
                '- Work: </work shift:1011560371267579942> \n'
                '- Pets: </pets care:1011560371171102768> \n'     
                '- Scratch: </scratch:1011560371267579934> \n'
                '- Stream: </stream:1011560371267579938> \n'
                '- Weekly: </weekly:1011560370948800549> \n'
                '- Monthly: </monthly:1011560370911072262> \n\n'
                '**Rumble Royale:** \n'
                '- Daily: </daily:975902717002285127> \n'
                '- Quests: </quests:1363578092911595732> \n'
                '- Weekly: </weekly:975902718570942464> \n\n'
                '**AuraColls:** \n'
                '- Daily: </daily:1465203396393828490> \n'
                '- Work: </work:1465203396393828491> \n'
                '- Pick: </pick:1465203396741959758> \n'
                '- Weekly: </weekly:1465203396393828493> \n\n'
                '**Others:** \n'
                '- Ghostly: `?daily` | `?weekly` \n'
                '- Mafia: </daily:1024791190941466677> \n\n'
                '**Vote Links:** \n'
                '- Dank Memer: </vote:1011560370994954286> \n'
                '- [OwO](https://top.gg/bot/408785106942164992/vote) \n'
                '- [AuraColls](https://top.gg/bot/1261363542867578910/vote) \n'
                '- [AuraPrime](https://top.gg/bot/1316827072655523911/vote) \n'
                '- [Reaction Bot](https://top.gg/bot/519287796549156864/vote) \n'
            )
        )
        embed.set_footer(
            text='BMTG | AURA',
            icon_url='https://cdn.discordapp.com/icons/1063458575667699832/a_00030a2bbe60e06071ad5b259360ea53.gif?size=1024&width=640&height=640'
        )
        # Sets the timestamp to current time
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Dailyrem(bot))
