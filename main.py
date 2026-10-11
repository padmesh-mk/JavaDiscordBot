import discord
from discord.ext import commands
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from console_logger import DiscordLogHandler

# Load environment variables early so we can read prefix
load_dotenv()
DEFAULT_PREFIX = os.getenv('PREFIX', '&')

def get_prefix(bot, message):
    # Support prefix and prefix followed by space
    return [DEFAULT_PREFIX, DEFAULT_PREFIX + ' ']

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.start_time = discord.utils.utcnow()
        
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None  # We have our own custom slash help command
        )

    async def setup_hook(self):
        logging.info('--- Starting Startup Sequence ---')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cogs_dir = os.path.join(base_dir, 'cogs')
        
        # Ensure cogs directory exists
        if not os.path.exists(cogs_dir):
            os.makedirs(cogs_dir)
            
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logging.info(f'✅ Loaded extension: {filename}')
                except Exception as e:
                    logging.error(f'❌ Failed to load extension {filename}: {e}')
        logging.info('--- Extensions Loaded ---')

    async def on_ready(self):
        logging.info(f'🚀 Logged in as {self.user.name} ({self.user.id})')
        try:
            # Sync commands globally (or per guild if specified)
            guild_id = os.getenv('GUILD_ID')
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                # Copy global commands to the guild to sync them immediately
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logging.info(f'✅ Synced {len(synced)} slash commands to Guild ID {guild_id}')
            else:
                synced = await self.tree.sync()
                logging.info(f'✅ Synced {len(synced)} slash commands globally')
        except Exception as e:
            logging.error(f'❌ Slash command sync error: {e}')
        logging.info('✨ Bot is fully ready and online!')

async def main():
    # Force UTF-8 output on Windows consoles to support emojis cleanly
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    TOKEN = os.getenv('TOKEN')
    WEBHOOK_URL = os.getenv("LOG_WEBHOOK_URL")
    
    # Configure Logging formatters and handlers
    formatter = logging.Formatter('%(asctime)s | %(levelname)s: %(message)s')
    
    # 1. Console stream handler (logs to stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # 2. Discord Webhook Log Handler
    if WEBHOOK_URL:
        try:
            handler = DiscordLogHandler(webhook_url=WEBHOOK_URL)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            await handler.start()
            logging.info("🦵 Discord bot logging has started.")
        except Exception as e:
            logging.error(f"❌ Failed to initialize DiscordLogHandler: {e}")
    else:
        logging.warning("⚠️ LOG_WEBHOOK_URL is not set in environment. Discord logging is disabled.")

    if not TOKEN:
        logging.error("ERROR: Please set your TOKEN in the .env file")
        return

    # Start bot
    bot = MyBot()
    async with bot:
        logging.info("🚀 Bot starting now...")
        try:
            await bot.start(TOKEN)
        except asyncio.CancelledError:
            pass

if __name__ == '__main__':
    asyncio.run(main())
