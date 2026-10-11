import discord
from discord.ext import tasks, commands
import os
import logging
import datetime
from zoneinfo import ZoneInfo

# Channel & Role configs
CHANNEL_ID_1 = 1431308807543197897
ROLE_ID_1 = 1362703328878002389
MESSAGE_1 = f"Hey <@&{ROLE_ID_1}>! Don't forget to send your cookie 🍪"

CHANNEL_ID_2 = 1356194205701116075
ROLE_ID_2 = 1360858589866233957
MESSAGE_2 = f"Hey <@&{ROLE_ID_2}>! Time to send Clover to Padmesh 🍀"

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity_index = 0
        
        self.activities = [
            discord.Activity(name='/help for commands', type=discord.ActivityType.watching),
            discord.Activity(name='events in BMTG', type=discord.ActivityType.playing),
            discord.Activity(name='members chatting', type=discord.ActivityType.listening),
            discord.Activity(name='cool updates rolling out!', type=discord.ActivityType.watching),
            discord.Activity(name='OwO', type=discord.ActivityType.playing),
            discord.Activity(name='music in VC', type=discord.ActivityType.listening),
            discord.Activity(name='BMTG for gaws', type=discord.ActivityType.watching),
            discord.Activity(name='Dank Memer', type=discord.ActivityType.playing),
            discord.Activity(name='commands with &', type=discord.ActivityType.listening),
            discord.Activity(name='BMTG on Youtube', type=discord.ActivityType.watching),
        ]
        
        # Get status from environment
        status_map = {
            'online': discord.Status.online,
            'idle': discord.Status.idle,
            'dnd': discord.Status.dnd,
            'do_not_disturb': discord.Status.dnd,
            'invisible': discord.Status.invisible,
            'offline': discord.Status.offline
        }
        self.activity_status = status_map.get(os.getenv('ACTIVITY_STATUS', 'online').lower(), discord.Status.online)

    @commands.Cog.listener()
    async def on_ready(self):
        # Start loops when bot is ready to ensure client is logged in
        if not self.hourly_uptime_log.is_running():
            self.hourly_uptime_log.start()
        if not self.activity_rotation.is_running():
            self.activity_rotation.start()
        if not self.daily_reminder.is_running():
            self.daily_reminder.start()
        logging.info('✅ Background loops have started.')

    def cog_unload(self):
        self.hourly_uptime_log.cancel()
        self.activity_rotation.cancel()
        self.daily_reminder.cancel()

    @tasks.loop(hours=1.0)
    async def hourly_uptime_log(self):
        # Log bot uptime every hour
        delta = discord.utils.utcnow() - self.bot.start_time
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        logging.info(f"⏱ Bot uptime: {delta.days}d {hours}h {minutes}m {seconds}s")

    @tasks.loop(seconds=10.0)
    async def activity_rotation(self):
        if not self.bot.user:
            return
        activity = self.activities[self.activity_index]
        try:
            await self.bot.change_presence(activity=activity, status=self.activity_status)
            self.activity_index = (self.activity_index + 1) % len(self.activities)
        except Exception as e:
            logging.error(f"Error rotating activity: {e}")

    # Daily Reminder Task — runs at 12:30 PM IST (Asia/Kolkata)
    @tasks.loop(time=datetime.time(hour=12, minute=30, tzinfo=ZoneInfo("Asia/Kolkata")))
    async def daily_reminder(self):
        logging.info('🔔 Reminder triggered!')
        
        channel1 = self.bot.get_channel(CHANNEL_ID_1)
        if not channel1:
            try:
                channel1 = await self.bot.fetch_channel(CHANNEL_ID_1)
            except Exception:
                pass
                
        if channel1:
            try:
                await channel1.send(MESSAGE_1)
            except Exception as e:
                logging.error(f"Failed to send Cookie reminder: {e}")
        else:
            logging.warning('❌ Cookie reminder channel not found.')

        channel2 = self.bot.get_channel(CHANNEL_ID_2)
        if not channel2:
            try:
                channel2 = await self.bot.fetch_channel(CHANNEL_ID_2)
            except Exception:
                pass
                
        if channel2:
            try:
                await channel2.send(MESSAGE_2)
            except Exception as e:
                logging.error(f"Failed to send Clover reminder: {e}")
        else:
            logging.warning('❌ Clover reminder channel not found.')

async def setup(bot):
    await bot.add_cog(Tasks(bot))
