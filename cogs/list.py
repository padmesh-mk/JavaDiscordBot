import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class ListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_user_id = 941902212303556618
        self.file_path = './list.json'

    # Slash Command Group /list
    list_group = app_commands.Group(name="list", description="Manage your personal list")

    def load_list(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_list(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def is_allowed(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.allowed_user_id

    @list_group.command(name="show", description="Show your to-buy list")
    async def show(self, interaction: discord.Interaction):
        if not self.is_allowed(interaction):
            return await interaction.response.send_message("❌ You can't use this command.", ephemeral=True)
            
        list_data = self.load_list()
        description = "\n".join(f"⇀ {item}" for item in list_data) if list_data else "No items in the list."
        
        embed = discord.Embed(
            title="Padmesh's To-Buy List!!",
            description=description,
            color=0x800080
        )
        embed.set_footer(text=f"Total Items: {len(list_data)} | Collector – Items: 94%")
        
        await interaction.response.send_message(embed=embed)

    @list_group.command(name="add", description="Add an item to the list")
    @app_commands.describe(item="Item to add")
    async def add(self, interaction: discord.Interaction, item: str):
        if not self.is_allowed(interaction):
            return await interaction.response.send_message("❌ You can't use this command.", ephemeral=True)
            
        list_data = self.load_list()
        if item in list_data:
            return await interaction.response.send_message(f"⚠️ `{item}` is already in the list.", ephemeral=True)
            
        list_data.append(item)
        self.save_list(list_data)
        await interaction.response.send_message(f"✅ Added `{item}` to your list.")

    @list_group.command(name="remove", description="Remove an item from the list")
    @app_commands.describe(item="Item to remove")
    async def remove(self, interaction: discord.Interaction, item: str):
        if not self.is_allowed(interaction):
            return await interaction.response.send_message("❌ You can't use this command.", ephemeral=True)
            
        list_data = self.load_list()
        if item not in list_data:
            return await interaction.response.send_message(f"❌ `{item}` not found in the list.", ephemeral=True)
            
        list_data.remove(item)
        self.save_list(list_data)
        await interaction.response.send_message(f"🗑️ Removed `{item}` from your list.")

async def setup(bot):
    await bot.add_cog(ListCog(bot))
