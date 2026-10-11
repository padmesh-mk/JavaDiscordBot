import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class LeaderboardView(discord.ui.View):
    def __init__(self, author_id, sorted_donations, bot, timeout=60.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.sorted_donations = sorted_donations
        self.bot = bot
        self.per_page = 10
        self.total_pages = max(1, (len(sorted_donations) + self.per_page - 1) // self.per_page)
        self.current_page = 0
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only you can interact with this leaderboard.", ephemeral=True)
            return False
        return True

    async def get_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        current_slice = self.sorted_donations[start:end]
        
        description_lines = []
        for index, (user_id_str, amount) in enumerate(current_slice):
            pos = start + index + 1
            medal = '🥇' if pos == 1 else '🥈' if pos == 2 else '🥉' if pos == 3 else '🔹'
            
            try:
                user = self.bot.get_user(int(user_id_str))
                if not user:
                    user = await self.bot.fetch_user(int(user_id_str))
                username = user.name if user else f"Unknown ({user_id_str})"
            except Exception:
                username = f"Unknown ({user_id_str})"
                
            description_lines.append(f"{medal} ` {amount:,} ` - {username}")
            
        description = "\n".join(description_lines) if description_lines else "No donations yet."
        
        total_donators = len(self.sorted_donations)
        total_donations_amount = sum(amount for _, amount in self.sorted_donations)

        embed = discord.Embed(
            title="OwO Donation Leaderboard",
            description=description,
            color=0x9B59B6
        )
        embed.add_field(name="Total Donators:", value=str(total_donators), inline=True)
        embed.add_field(name="Total Donations:", value=f"{total_donations_amount:,}", inline=True)
        embed.set_footer(text=f"Page {self.current_page + 1} of {self.total_pages}")
        
        return embed

    @discord.ui.button(label='◀️', style=discord.ButtonStyle.secondary, custom_id='prev_lb')
    async def prev_lb(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % self.total_pages
        embed = await self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='▶️', style=discord.ButtonStyle.secondary, custom_id='next_lb')
    async def next_lb(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % self.total_pages
        embed = await self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        # Clear buttons on timeout
        if self.message:
            try:
                await self.message.edit(view=None)
            except discord.HTTPException:
                pass

class OwoDono(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.donation_file = './donations.json'
        self.log_channel_id = 1381822531681517629

    def load_donations(self):
        if os.path.exists(self.donation_file):
            try:
                with open(self.donation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_donations(self, data):
        with open(self.donation_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Top-level group /owo
    owo = app_commands.Group(name="owo", description="Manage and view OwO donations")
    # Subgroup /owo dono
    dono = app_commands.Group(name="dono", description="OwO Donation Tools", parent=owo)
    
    @dono.command(name="add", description="Manually add a donation")
    @app_commands.describe(user="User who donated", amount="Amount donated")
    async def add(self, interaction: discord.Interaction, user: discord.User, amount: int):
        # Check administrator permission
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)

        await interaction.response.defer(ephemeral=False)
        donations = self.load_donations()
        
        user_id_str = str(user.id)
        donations[user_id_str] = donations.get(user_id_str, 0) + amount
        self.save_donations(donations)

        avatar_url = user.display_avatar.url
        reply_embed = discord.Embed(color=0x2ECC71)
        reply_embed.set_author(name=f"{user.name}'s OwO Donation", icon_url=avatar_url)
        reply_embed.add_field(name="Your Donation", value=f"• `{amount:,}`", inline=False)
        reply_embed.add_field(
            name="Summary",
            value=f"• **Amount added:** `{amount:,}`\n• **Total donated:** `{donations[user_id_str]:,}`",
            inline=False
        )
        reply_embed.set_footer(text="Thanks for Donating <3")

        log_embed = discord.Embed(color=0x00AE86)
        log_embed.set_author(name=f"{user.name}'s OwO Donation", icon_url=avatar_url)
        log_embed.add_field(
            name="New Donation",
            value=f"• **Amount added:** `{amount:,}`\n• **Total donated:** `{donations[user_id_str]:,}`",
            inline=False
        )
        log_embed.add_field(name="Manually Added By:", value=f"<@{interaction.user.id}> in <#{interaction.channel.id}>", inline=False)

        await interaction.followup.send(embed=reply_embed)

        log_channel = interaction.guild.get_channel(self.log_channel_id)
        if log_channel:
            try:
                await log_channel.send(embed=log_embed)
            except Exception:
                pass

    @dono.command(name="remove", description="Remove a donation amount from a user")
    @app_commands.describe(user="User to remove donation from", amount="Amount to remove")
    async def remove(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)

        await interaction.response.defer(ephemeral=False)
        donations = self.load_donations()
        
        user_id_str = str(user.id)
        current = donations.get(user_id_str, 0)

        if amount > current:
            return await interaction.followup.send(
                content=f"❌ Cannot remove `{amount:,}` from <@{user.id}>. They only have `{current:,}` donated.",
                ephemeral=True
            )

        donations[user_id_str] = current - amount
        if donations[user_id_str] <= 0:
            if user_id_str in donations:
                del donations[user_id_str]
        self.save_donations(donations)

        avatar_url = user.display_avatar.url
        reply_embed = discord.Embed(color=0xE74C3C)
        reply_embed.set_author(name=f"{user.name}'s OwO Donation", icon_url=avatar_url)
        reply_embed.add_field(name="Donation Removed", value=f"• `{amount:,}`", inline=False)
        reply_embed.add_field(
            name="Summary",
            value=f"• **Amount removed:** `{amount:,}`\n• **Remaining total:** `{(donations.get(user_id_str, 0)):,}`",
            inline=False
        )
        reply_embed.set_footer(text="Donation adjusted manually.")

        log_embed = discord.Embed(color=0xC0392B)
        log_embed.set_author(name=f"{user.name}'s OwO Donation", icon_url=avatar_url)
        log_embed.add_field(
            name="Donation Removed",
            value=f"• **Amount removed:** `{amount:,}`\n• **Remaining total:** `{(donations.get(user_id_str, 0)):,}`",
            inline=False
        )
        log_embed.add_field(name="Removed By:", value=f"<@{interaction.user.id}> in <#{interaction.channel.id}>", inline=False)

        await interaction.followup.send(embed=reply_embed)

        log_channel = interaction.guild.get_channel(self.log_channel_id)
        if log_channel:
            try:
                await log_channel.send(embed=log_embed)
            except Exception:
                pass

    @dono.command(name="check", description="Check total donations by a user")
    @app_commands.describe(user="User to check")
    async def check(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=False)
        donations = self.load_donations()
        
        user_id_str = str(user.id)
        total = donations.get(user_id_str, 0)

        embed = discord.Embed(color=0xCCCCFF)
        embed.set_author(name=f"{user} ({user.id})", icon_url=user.display_avatar.url)
        embed.add_field(name="Total Donations:", value=f"`{total:,}`", inline=False)

        await interaction.followup.send(embed=embed)

    @dono.command(name="lb", description="Show top 10 donation leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        donations = self.load_donations()
        
        sorted_donations = sorted(donations.items(), key=lambda x: x[1], reverse=True)
        
        view = LeaderboardView(
            author_id=interaction.user.id,
            sorted_donations=sorted_donations,
            bot=self.bot,
            timeout=60.0
        )
        embed = await view.get_embed()
        
        message = await interaction.followup.send(embed=embed, view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(OwoDono(bot))
