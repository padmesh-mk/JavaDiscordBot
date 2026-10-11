import discord
from discord.ext import commands
from discord import app_commands

class HelpView(discord.ui.View):
    def __init__(self, author_id, timeout=60.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.current_page = 1
        self.total_pages = 4
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command user can navigate this help menu.", ephemeral=True)
            return False
        return True

    def get_embed(self):
        embed = discord.Embed(color=0x00c0ff)
        embed.timestamp = discord.utils.utcnow()

        if self.current_page == 1:
            embed.title = 'Help Menu - General Slash Commands'
            embed.description = (
                '</help:1317454985801502803>\n'
                '⤷ Displays this help menu\n'
                '</ping:1317454985801502804>\n'
                '⤷ Check if the bot is online\n'
                '</owo dono check:1387129068612227165>\n'
                '⤷ To check an user OwO Donations\n'
                '</owo dono lb:1387129068612227165>\n'
                '⤷ To display top 10 OwO Donations'
            )
            embed.set_footer(text='Page 1 of 4')
        elif self.current_page == 2:
            embed.title = 'Help Menu - General Prefix Commands'
            embed.description = (
                '`&ping`\n'
                '⤷ Check if the bot is online\n'
                '`&uptime`\n'
                '⤷ Check the uptime of bot\n'
                '`&membercount | &mc`\n'
                '⤷ Check the Guild Member Count\n'
                '`&rem`\n'
                '⤷ Daily reminder for few bots'
            )
            embed.set_footer(text='Page 2 of 4')
        elif self.current_page == 3:
            embed.title = 'Help Menu - Perks Prefix Commands'
            embed.description = (
                '`&kik [user][reason]`\n'
                '⤷ Fake kick an user\n'
                '`&bon [user][reason]`\n'
                '⤷ Fake ban an user'
            )
            embed.set_footer(text='Page 3 of 4')
        elif self.current_page == 4:
            embed.title = 'Help Menu - Admin Commands'
            embed.description = (
                '`&bat [message]`\n'
                '⤷ Staff battle ping'
            )
            embed.set_footer(text='Page 4 of 4')

        return embed

    @discord.ui.button(label='⏮️ First', style=discord.ButtonStyle.primary)
    async def first_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        await interaction.response.edit_message(embed=self.get_embed())

    @discord.ui.button(label='⬅️ Back', style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
        await interaction.response.edit_message(embed=self.get_embed())

    @discord.ui.button(label='➡️ Forward', style=discord.ButtonStyle.secondary)
    async def forward_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages:
            self.current_page += 1
        await interaction.response.edit_message(embed=self.get_embed())

    @discord.ui.button(label='⏭️ Last', style=discord.ButtonStyle.primary)
    async def last_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = self.total_pages
        await interaction.response.edit_message(embed=self.get_embed())

    async def on_timeout(self):
        # Disable all buttons
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help', description='Displays a help menu with information about commands.')
    async def help_command(self, interaction: discord.Interaction):
        view = HelpView(author_id=interaction.user.id, timeout=60.0)
        embed = view.get_embed()
        
        await interaction.response.send_message(embed=embed, view=view)
        # Save reference to message to disable buttons on timeout
        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(Help(bot))
