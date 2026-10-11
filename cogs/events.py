import discord
from discord.ext import commands
import json
import os
import re

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = 1096432513834045441
        self.leave_channel_id = 1270059585448837202
        self.watched_channel_ids = [
            1309391051068276776,
            1309395345179938865,
            1314472110038712391,
            1354518893154140170
        ]
        self.your_user_id = 941902212303556618
        self.log_channel_id = 1381822531681517629
        self.donation_file = './donations.json'

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

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(self.welcome_channel_id)
        if not channel:
            return

        welcome_embed = discord.Embed(
            title="Welcome to BMTG ↬ Dank・OwO・Giveaways・Events | AURA!",
            description=(
                f"### Hey <@{member.id}>\n\n"
                "- Check out my YouTube Videos <:bmtg_Subscribe:1096508185365450842> on https://discord.com/channels/1063458575667699832/1064194064934764606\n"
                "- Grab your desired roles and more from <id:customize> and https://discord.com/channels/1063458575667699832/1309214562213691443, you can change them anytime!\n"
                "- Make sure to check out https://discord.com/channels/1063458575667699832/1105157414992478268\n\n"
                "Thanks for joining <:bmtg_ty_thankyou:1217690109701525524>\n"
                "We hope you enjoy your stay."
            ),
            color=0x00ffe5
        )
        welcome_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        if member.guild.icon:
            welcome_embed.set_thumbnail(url=member.guild.icon.url)
        welcome_embed.set_footer(text=f"You are our {member.guild.member_count} member!")
        welcome_embed.timestamp = discord.utils.utcnow()

        try:
            await channel.send(embed=welcome_embed)
        except Exception as e:
            print("Failed to send welcome embed:", e)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.get_channel(self.leave_channel_id)
        if not channel:
            return

        leave_embed = discord.Embed(
            description=f"Unfortunately, <@{member.id}> has left **BMTG ↬ Dank・OwO・Giveaways・Events | AURA!**",
            color=0xff0000
        )
        leave_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        leave_embed.set_thumbnail(url=member.display_avatar.url)
        leave_embed.set_footer(text=f"We now have {member.guild.member_count} members.")
        leave_embed.timestamp = discord.utils.utcnow()

        try:
            await channel.send(embed=leave_embed)
        except Exception as e:
            print("Failed to send leave embed:", e)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        try:
            if after.channel.id not in self.watched_channel_ids:
                return
            if not after.author or not after.author.bot or 'cowoncy' not in after.content:
                return
            if before.content == after.content:
                return

            parts = after.content.split(' ')
            if len(parts) < 8:
                return

            # Extract donor ID
            donor_parts = parts[2].split('<@')
            if len(donor_parts) < 2:
                return
            donor_id_str = donor_parts[1].split('>')[0]
            if not donor_id_str.isdigit():
                return

            # Extract amount
            amount_str = parts[4].replace('**', '').replace(',', '')
            try:
                amount = int(amount_str)
            except ValueError:
                return

            # Extract recipient ID
            recipient_parts = parts[7].split('<@')
            if len(recipient_parts) < 2:
                return
            recipient_id_str = recipient_parts[1].split('>')[0].replace('**!', '')

            if int(recipient_id_str) != self.your_user_id:
                return

            # Save donation
            donations = self.load_donations()
            donations[donor_id_str] = donations.get(donor_id_str, 0) + amount
            self.save_donations(donations)

            donor_user = await self.bot.fetch_user(int(donor_id_str))
            log_channel = after.guild.get_channel(self.log_channel_id)

            if not donor_user or not log_channel:
                return

            # User Reply Embed
            reply_embed = discord.Embed(color=0x2ECC71)
            reply_embed.set_author(name=f"{donor_user.name}'s OwO Donation", icon_url=donor_user.display_avatar.url)
            reply_embed.add_field(name="Your Donation", value=f"• `{amount:,}`", inline=False)
            reply_embed.add_field(
                name="Summary",
                value=f"• **Amount added:** `{amount:,}`\n• **Total donated:** `{donations[donor_id_str]:,}`",
                inline=False
            )
            reply_embed.set_footer(text="Thanks for Donating <3")

            # Admin Log Embed
            log_embed = discord.Embed(color=0x00AE86)
            log_embed.set_author(name=f"{donor_user.name}'s OwO Donation", icon_url=donor_user.display_avatar.url)
            log_embed.add_field(
                name="New Donation",
                value=f"• **Amount added:** `{amount:,}`\n• **Total donated:** `{donations[donor_id_str]:,}`",
                inline=False
            )
            log_embed.add_field(name="Donated In:", value=f"<#{after.channel.id}>", inline=False)

            # React with ✅
            await after.add_reaction('✅')
            # Reply to the message
            await after.reply(embed=reply_embed)
            # Log to admin channel
            await log_channel.send(embed=log_embed)

        except Exception as err:
            print(f"❌ Donation Logger Error: {str(err)}")

async def setup(bot):
    await bot.add_cog(Events(bot))
