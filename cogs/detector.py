import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import re
import logging
import time
import datetime
from zoneinfo import ZoneInfo
from collections import Counter

CONFIG_FILE = './detector_config.json'
ACTIVE_CAPTCHAS_FILE = './active_captchas.json'
CAPTCHA_LOGS_FILE = './captcha_logs.json'

OWNER_ID = 941902212303556618

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading {filepath}: {e}")
            return default
    return default

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving {filepath}: {e}")

def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == OWNER_ID

def get_stats_for_range(guild_id: str, time_filter: str, specific_date: str = None) -> list[dict]:
    stats = load_json(CAPTCHA_LOGS_FILE, [])
    guild_stats = [s for s in stats if str(s.get("guild_id")) == str(guild_id)]
    now = datetime.datetime.now()
    
    def get_midnight(dt: datetime.datetime) -> datetime.datetime:
        return datetime.datetime(dt.year, dt.month, dt.day)
        
    filtered = []
    if specific_date:
        try:
            target_dt = datetime.datetime.strptime(specific_date, "%Y-%m-%d")
            start_ts = target_dt.timestamp()
            end_ts = (target_dt + datetime.timedelta(days=1)).timestamp()
            for s in guild_stats:
                if start_ts <= s["timestamp"] < end_ts:
                    filtered.append(s)
        except ValueError:
            pass
    elif time_filter == "today":
        start_ts = get_midnight(now).timestamp()
        for s in guild_stats:
            if s["timestamp"] >= start_ts:
                filtered.append(s)
    elif time_filter == "yesterday":
        today_midnight = get_midnight(now)
        start_ts = (today_midnight - datetime.timedelta(days=1)).timestamp()
        end_ts = today_midnight.timestamp()
        for s in guild_stats:
            if start_ts <= s["timestamp"] < end_ts:
                filtered.append(s)
    elif time_filter == "past_7_days":
        start_ts = (now - datetime.timedelta(days=7)).timestamp()
        for s in guild_stats:
            if s["timestamp"] >= start_ts:
                filtered.append(s)
    else:  # all_time
        filtered = guild_stats
        
    return filtered

def get_leaderboard_data(guild: discord.Guild, time_filter: str, specific_date: str = None) -> list[tuple[str, str, int]]:
    guild_id = str(guild.id)
    filtered_stats = get_stats_for_range(guild_id, time_filter, specific_date)
    counter = Counter()
    name_map = {}
    for s in filtered_stats:
        user_id_str = s["user_id"]
        try:
            user_id_int = int(user_id_str)
        except ValueError:
            continue
        member = guild.get_member(user_id_int)
        if member:
            counter[user_id_str] += 1
            name_map[user_id_str] = member.display_name
        else:
            counter[user_id_str] += 1
            name_map[user_id_str] = s.get("username", f"User {user_id_str}")
        
    sorted_users = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return [(uid, name_map[uid], count) for uid, count in sorted_users]

class SearchDateModal(discord.ui.Modal, title="Search Specific Date"):
    date_input = discord.ui.TextInput(label="Date (YYYY-MM-DD)", placeholder="e.g. 2026-06-09", required=True)
    def __init__(self, view):
        super().__init__()
        self.view = view
    async def on_submit(self, interaction: discord.Interaction):
        raw = self.date_input.value.strip()
        try:
            datetime.datetime.strptime(raw, "%Y-%m-%d")
            self.view.specific_date = raw
            self.view.page = 0
            await self.view.update_view(interaction)
        except ValueError:
            await interaction.response.send_message("Invalid date format. Please use YYYY-MM-DD.", ephemeral=True)

class LeaderboardView(discord.ui.LayoutView):
    PER_PAGE = 10
    def __init__(self, guild: discord.Guild, request_user: discord.User, time_filter: str = "today", specific_date: str = None, page: int = 0):
        super().__init__(timeout=120)
        self.guild = guild
        self.guild_id = str(guild.id)
        self.request_user = request_user
        self.time_filter = time_filter
        self.specific_date = specific_date
        self.page = page
        self.build_view()
        
    def build_view(self):
        self.clear_items()
        lb_data = get_leaderboard_data(self.guild, self.time_filter, self.specific_date)
        total_pages = (len(lb_data) + self.PER_PAGE - 1) // self.PER_PAGE or 1
        self.page = max(0, min(self.page, total_pages - 1))
        
        start = self.page * self.PER_PAGE
        medal_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        
        filter_labels = {
            "today": "Today",
            "yesterday": "Yesterday",
            "past_7_days": "Past 7 Days",
            "all_time": "All Time"
        }
        
        filter_title = f"Date: {self.specific_date}" if self.specific_date else filter_labels.get(self.time_filter, "All Time")
        title = f"🚨 Captcha Leaderboard ({filter_title})"
        
        user_rank = 0
        user_count = 0
        for idx, (uid, name, count) in enumerate(lb_data, start=1):
            if uid == str(self.request_user.id):
                user_rank = idx
                user_count = count
                break
                
        if user_rank > 0:
            user_info = f"**{self.request_user.display_name}**: `{user_count}` captchas | Rank: `#{user_rank}`"
        else:
            user_info = f"**{self.request_user.display_name}**: No captchas yet!"
            
        lines = [f"# {title}", user_info, ""]
        lb_lines = []
        for idx, (uid, name, count) in enumerate(lb_data[start:start + self.PER_PAGE], start=start + 1):
            medal = medal_map.get(idx, f"`#{idx}`")
            lb_lines.append(f"{medal} `{count}` captchas – **{name}** (<@{uid}>)")
            
        lines.append("\n".join(lb_lines) if lb_lines else "_No captchas recorded for this period!_")
        lines.append(f"\n-# Page {self.page + 1}/{total_pages} • {filter_title}")
        
        body = "\n".join(lines)
        container = discord.ui.Container(accent_color=0xFFD700)
        container.add_item(discord.ui.TextDisplay(body))
        container.add_item(discord.ui.Separator())
        
        options = [
            discord.SelectOption(label="Today", value="today", default=self.time_filter == "today" and not self.specific_date, emoji="📅"),
            discord.SelectOption(label="Yesterday", value="yesterday", default=self.time_filter == "yesterday" and not self.specific_date, emoji="🗓️"),
            discord.SelectOption(label="Past 7 Days", value="past_7_days", default=self.time_filter == "past_7_days" and not self.specific_date, emoji="📈"),
            discord.SelectOption(label="All Time", value="all_time", default=self.time_filter == "all_time" and not self.specific_date, emoji="🏆"),
        ]
        
        mode_select = discord.ui.Select(placeholder="Select time filter...", options=options)
        mode_select.callback = self.on_filter_change
        container.add_item(discord.ui.ActionRow(mode_select))
        
        prev_btn = discord.ui.Button(label="Back", style=discord.ButtonStyle.gray, emoji="<:ap_backward:1382775479202746378>", disabled=self.page == 0)
        prev_btn.callback = self.on_prev
        
        next_btn = discord.ui.Button(label="Next", style=discord.ButtonStyle.gray, emoji="<:ap_forward:1382775383371419790>", disabled=self.page >= total_pages - 1)
        next_btn.callback = self.on_next
        
        search_btn = discord.ui.Button(label="Search Date", style=discord.ButtonStyle.blurple, emoji="<:ap_date:1382718456000024631>")
        search_btn.callback = self.on_search_click
        
        container.add_item(discord.ui.ActionRow(prev_btn, next_btn, search_btn))
        self.add_item(container)
        
    async def update_view(self, interaction: discord.Interaction):
        self.build_view()
        await interaction.response.edit_message(view=self)
        
    async def on_filter_change(self, interaction: discord.Interaction):
        self.time_filter = interaction.data["values"][0]
        self.specific_date = None
        self.page = 0
        self.build_view()
        await interaction.response.edit_message(view=self)
        
    async def on_prev(self, interaction: discord.Interaction):
        self.page -= 1
        self.build_view()
        await interaction.response.edit_message(view=self)
        
    async def on_next(self, interaction: discord.Interaction):
        self.page += 1
        self.build_view()
        await interaction.response.edit_message(view=self)
        
    async def on_search_click(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchDateModal(self))

class Detector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owo_bot_id = 408785106942164992
        
        # Regexes for pattern matching (uses [⚠️\u26a0] for variation selector safety)
        self.type1_regex = re.compile(
            r"[⚠️\u26a0]\s*\|\s*<@!?(\d+)>\s*!\s*Please complete your captcha to verify that you are human!",
            re.IGNORECASE
        )
        self.type2_regex = re.compile(
            r"[⚠️\u26a0]\s*\|\s*<@!?(\d+)>\s*,\s*are you a real human\?",
            re.IGNORECASE
        )
        self.type3_regex = re.compile(
            r"[⚠️\u26a0]\s*\|\s*([^,]+),\s*Beep Boop\.\s*Please DM me",
            re.IGNORECASE
        )

    # Top-level group /de
    de = app_commands.Group(name="de", description="...")
    # Subgroup /de settings
    settings = app_commands.Group(name="settings", description="...", parent=de)

    @settings.command(name="add", description="...")
    @app_commands.describe(channel="Channel to monitor", mute_role="Role to give when captcha is active", unmute_role="Role to give when captcha is solved")
    async def settings_add(self, interaction: discord.Interaction, channel: discord.TextChannel, mute_role: discord.Role, unmute_role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        if not is_owner(interaction):
            return await interaction.followup.send("❌ You do not have permission to use this command.", ephemeral=True)
            
        config = load_json(CONFIG_FILE, {"log_channel_id": None, "categories": []})
        
        # Check if channel is already configured
        for cat in config["categories"]:
            if cat["channel_id"] == channel.id:
                return await interaction.followup.send(f"⚠️ Channel <#{channel.id}> is already configured. Remove it first if you wish to re-add.", ephemeral=True)
                
        new_cat = {
            "channel_id": channel.id,
            "mute_role_id": mute_role.id,
            "unmute_role_id": unmute_role.id
        }
        config["categories"].append(new_cat)
        save_json(CONFIG_FILE, config)
        
        await interaction.followup.send(
            f"✅ Configured channel <#{channel.id}>:\n"
            f"• **Mute Role**: <@&{mute_role.id}>\n"
            f"• **Unmute Role**: <@&{unmute_role.id}>",
            ephemeral=True
        )

    @settings.command(name="remove", description="...")
    @app_commands.describe(index="Index of configuration to remove (starting at 1)")
    async def settings_remove(self, interaction: discord.Interaction, index: int):
        await interaction.response.defer(ephemeral=True)
        if not is_owner(interaction):
            return await interaction.followup.send("❌ You do not have permission to use this command.", ephemeral=True)
            
        config = load_json(CONFIG_FILE, {"log_channel_id": None, "categories": []})
        categories = config["categories"]
        
        if index < 1 or index > len(categories):
            return await interaction.followup.send(f"❌ Invalid index `{index}`. Total configured: {len(categories)}.", ephemeral=True)
            
        removed = categories.pop(index - 1)
        save_json(CONFIG_FILE, config)
        
        await interaction.followup.send(f"🗑️ Removed configuration for channel <#{removed['channel_id']}>.", ephemeral=True)

    @settings.command(name="show", description="...")
    async def settings_show(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not is_owner(interaction):
            return await interaction.followup.send("❌ You do not have permission to use this command.", ephemeral=True)
            
        config = load_json(CONFIG_FILE, {"log_channel_id": None, "categories": []})
        categories = config["categories"]
        
        if not categories:
            return await interaction.followup.send("ℹ️ No categories are currently configured.", ephemeral=True)
            
        lines = ["## ⚙️ Captcha Detector Settings"]
        for idx, cat in enumerate(categories, 1):
            lines.append(
                f"**Category {idx}:**\n"
                f"• Channel: <#{cat['channel_id']}>\n"
                f"• Mute Role: <@&{cat['mute_role_id']}>\n"
                f"• Unmute Role: <@&{cat['unmute_role_id']}>"
            )
            
        await interaction.followup.send("\n".join(lines), ephemeral=True)

    @de.command(name="log", description="...")
    @app_commands.describe(channel="Channel to send logs to")
    async def log_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        await interaction.response.defer(ephemeral=True)
        if not is_owner(interaction):
            return await interaction.followup.send("❌ You do not have permission to use this command.", ephemeral=True)
            
        config = load_json(CONFIG_FILE, {"log_channel_id": None, "categories": []})
        
        if channel:
            config["log_channel_id"] = channel.id
            save_json(CONFIG_FILE, config)
            await interaction.followup.send(f"✅ Log channel successfully set to <#{channel.id}>.", ephemeral=True)
        else:
            current_log_channel = config.get("log_channel_id")
            if current_log_channel:
                await interaction.followup.send(f"📢 Logs are currently sent to <#{current_log_channel}>.", ephemeral=True)
            else:
                await interaction.followup.send("📢 No log channel configured yet. Use `/de log channel:#channel` to configure one.", ephemeral=True)

    @de.command(name="top", description="...")
    async def top_cmd(self, interaction: discord.Interaction):
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            
        await interaction.response.defer()
        view = LeaderboardView(interaction.guild, interaction.user)
        message = await interaction.followup.send(view=view)
        view.message = message

    # ─── Event Monitoring ─────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.check_and_process_captcha(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return
        await self.check_and_process_captcha(after)

    async def check_and_process_captcha(self, message: discord.Message):
        if not message.guild or not message.author:
            return
        if message.author.id != self.owo_bot_id:
            return
            
        config = load_json(CONFIG_FILE, {"log_channel_id": None, "categories": []})
        channel_config = None
        for cat in config["categories"]:
            if cat["channel_id"] == message.channel.id:
                channel_config = cat
                break
                
        if not channel_config:
            return
            
        # Strip zero-width spaces (\u200b, \u200c, \u200d, \ufeff) and asterisks to beat obfuscation
        clean_content = re.sub(r'[\u200b-\u200d\ufeff]', '', message.content).replace('*', '')
        
        # Detect target user
        target_user = None
        
        # Check Type 1
        m1 = self.type1_regex.search(clean_content)
        if m1:
            user_id = int(m1.group(1))
            target_user = message.guild.get_member(user_id)
            if not target_user:
                try:
                    target_user = await message.guild.fetch_member(user_id)
                except Exception:
                    pass
                    
        # Check Type 2
        m2 = self.type2_regex.search(clean_content)
        if m2 and not target_user:
            user_id = int(m2.group(1))
            target_user = message.guild.get_member(user_id)
            if not target_user:
                try:
                    target_user = await message.guild.fetch_member(user_id)
                except Exception:
                    pass
                    
        # Check Type 3
        m3 = self.type3_regex.search(clean_content)
        if m3 and not target_user:
            username = m3.group(1).strip()
            target_user = discord.utils.find(
                lambda m: m.name.lower() == username.lower() or 
                          m.display_name.lower() == username.lower() or 
                          (m.nick and m.nick.lower() == username.lower()), 
                message.guild.members
            )
            
        if not target_user:
            return
            
        # Prevent double processing of the same captcha message
        active_captchas = load_json(ACTIVE_CAPTCHAS_FILE, {})
        msg_id_str = str(message.id)
        if msg_id_str in active_captchas:
            return
            
        await self.apply_captcha_mute(message, target_user, channel_config, config.get("log_channel_id"))

    async def apply_captcha_mute(self, message: discord.Message, user: discord.Member, channel_config: dict, log_channel_id: int):
        mute_role_id = channel_config["mute_role_id"]
        unmute_role_id = channel_config["unmute_role_id"]
        
        mute_role = message.guild.get_role(mute_role_id)
        unmute_role = message.guild.get_role(unmute_role_id)
        
        if not mute_role:
            logging.error(f"[Detector] Mute role {mute_role_id} not found in guild.")
            return
            
        # 1. Remove unmute role if present
        if unmute_role and unmute_role in user.roles:
            try:
                await user.remove_roles(unmute_role, reason="New captcha detected, removing unmute role")
            except Exception as e:
                logging.error(f"[Detector] Failed to remove unmute role from {user}: {e}")
                
        # 2. Add mute role
        try:
            await user.add_roles(mute_role, reason="Captcha detected, applying mute role")
        except Exception as e:
            logging.error(f"[Detector] Failed to add mute role to {user}: {e}")
            
        # 3. Send notification message pinging the user
        notification_message = None
        try:
            notification_message = await message.channel.send(
                content=f"Hey <@{user.id}>, you have been muted. React with the 😂 emoji above to get unmuted!"
            )
            await notification_message.add_reaction("😂")
        except Exception as e:
            logging.error(f"[Detector] Failed to send notification or add reaction: {e}")
            
        # 5. Save to active_captchas.json (map both message IDs)
        active_captchas = load_json(ACTIVE_CAPTCHAS_FILE, {})
        captcha_entry = {
            "user_id": user.id,
            "channel_id": message.channel.id,
            "mute_role_id": mute_role_id,
            "unmute_role_id": unmute_role_id,
            "captcha_msg_id": message.id,
            "notif_msg_id": notification_message.id if notification_message else None
        }
        active_captchas[str(message.id)] = captcha_entry
        if notification_message:
            active_captchas[str(notification_message.id)] = captcha_entry
        save_json(ACTIVE_CAPTCHAS_FILE, active_captchas)
        
        # 6. Log occurrence to historical logs
        logs = load_json(CAPTCHA_LOGS_FILE, [])
        logs.append({
            "guild_id": str(message.guild.id),
            "user_id": str(user.id),
            "username": user.display_name,
            "timestamp": time.time()
        })
        save_json(CAPTCHA_LOGS_FILE, logs)
        
        # 7. Send log message: <@user> got [muted](message link)!
        if log_channel_id:
            log_channel = message.guild.get_channel(log_channel_id)
            if log_channel:
                try:
                    await log_channel.send(
                        content=f"<@{user.id}> got [muted]({message.jump_url})!",
                        allowed_mentions=discord.AllowedMentions.none()
                    )
                except Exception as e:
                    logging.error(f"[Detector] Failed to send log: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
            
        # Check if message is in active_captchas
        active_captchas = load_json(ACTIVE_CAPTCHAS_FILE, {})
        msg_id_str = str(payload.message_id)
        if msg_id_str not in active_captchas:
            return
            
        captcha_data = active_captchas[msg_id_str]
        
        # Check if the reacting user matches the captcha recipient
        if payload.user_id != captcha_data["user_id"]:
            return
            
        # Unmute
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
            
        member = guild.get_member(payload.user_id)
        if not member:
            try:
                member = await guild.fetch_member(payload.user_id)
            except Exception:
                return
                
        mute_role_id = captcha_data["mute_role_id"]
        unmute_role_id = captcha_data["unmute_role_id"]
        
        mute_role = guild.get_role(mute_role_id)
        unmute_role = guild.get_role(unmute_role_id)
        
        # 1. Remove mute role
        if mute_role and mute_role in member.roles:
            try:
                await member.remove_roles(mute_role, reason="User reacted to captcha, removing mute role")
            except Exception as e:
                logging.error(f"[Detector] Failed to remove mute role from {member}: {e}")
                
        # 2. Add unmute role
        if unmute_role:
            try:
                await member.add_roles(unmute_role, reason="User reacted to captcha, adding unmute role")
            except Exception as e:
                logging.error(f"[Detector] Failed to add unmute role to {member}: {e}")
                
        # 3. Delete notification message if it exists
        notif_msg_id = captcha_data.get("notif_msg_id")
        if notif_msg_id:
            channel = guild.get_channel(payload.channel_id)
            if channel:
                try:
                    notif_msg = await channel.fetch_message(notif_msg_id)
                    await notif_msg.delete()
                except Exception:
                    pass
                    
        # 4. Clean up both keys in active_captchas
        captcha_msg_id = captcha_data.get("captcha_msg_id")
        if str(captcha_msg_id) in active_captchas:
            del active_captchas[str(captcha_msg_id)]
        if notif_msg_id and str(notif_msg_id) in active_captchas:
            del active_captchas[str(notif_msg_id)]
        if msg_id_str in active_captchas:
            del active_captchas[msg_id_str]
        save_json(ACTIVE_CAPTCHAS_FILE, active_captchas)
        
        # 5. Send log: <@user> got [unmuted](original captcha link)!
        config = load_json(CONFIG_FILE, {"log_channel_id": None, "categories": []})
        log_channel_id = config.get("log_channel_id")
        
        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                try:
                    await log_channel.send(
                        content=f"<@{member.id}> got unmuted!",
                        allowed_mentions=discord.AllowedMentions.none()
                    )
                except Exception as e:
                    logging.error(f"[Detector] Failed to send log: {e}")

async def setup(bot):
    await bot.add_cog(Detector(bot))
