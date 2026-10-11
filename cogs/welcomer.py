import discord
from discord.ext import commands
from discord import app_commands
import os, json, random

CONFIG_FILE = "welcomer_channel.json"

WELCOME_MESSAGES = [
  "🎮 {user} joined the game!",
  "🎁 {user} is here for the giveaways!",
  "🔥 {user} entered the arena!",
  "👾 {user} just spawned in!",
  "🎊 Events just got better with {user}!",
  "🕹️ {user} joined the squad!",
  "🎉 {user} unlocked the welcome badge!",
  "💫 {user} has arrived. Let’s vibe!",
  "⚡ Power-up! {user} has joined the realm!",
  "🧩 A new challenger appears: {user}!",
  "🎮 {user} just picked 'Legendary' difficulty!",
  "🏹 {user} is ready for quests and chaos!",
  "🧙 {user} casted a join spell!",
  "🪄 Welcome, {user}, to the whole new dimension!",
  "🎯 {user} just hit the jackpot - welcome!",
  "💥 {user} entered the giveaway battlefield!",
  "👑 All rise! {user} has joined the kingdom!",
  "🌀 {user} just warped into the event zone!",
  
  "🎉 {user} just dropped in. Hide the snacks!",
  "🔍 Who summoned {user}?",
  "🧍 {user} has entered the simulation.",
  "🚪 {user} opened the wrong door… and stayed.",
  "😬 {user} just joined. Who let them in?",
  "📸 New face alert: {user}",
  "🫠 {user} is here. We were doing fine too.",
  "🧢 {user} arrived. Cap detected.",
  "📉 Server IQ now adjusting for {user}.",
  "🎭 {user} joined. Let the acting begin.",
  "🥴 {user} walked in like a lag spike.",
  "🪄 {user} appeared! Magically annoying.",
  "🐸 {user} hopped in. Ribbit vibes.",
  "🧃 {user} came in juicy. No pulp.",
  "🌚 {user} landed. Chaos moon rising.",
  "⚠️ Caution: {user} entered unsupervised.",
  "🎮 {user} spawned with default settings.",
  "📦 {user} delivered. Return window closed.",
  "💅 {user} joined. Drama mode ON.",
  "🤐 {user} is here. Don’t ask why.",
  "🛸 {user} arrived. Beep bop who dis?",
  "🧃 {user} is here. No refills.",
  "🛑 Stop scrolling — it’s {user}.",
  "🐔 {user} dropped in. Chicken run vibes.",
  "🕶️ {user} joined. Too cool to care.",
  "🔇 {user} joined silently… suspicious.",
  "👞 {user} just stepped on the server rug.",
  "🥸 {user} joined. Pretend to be normal.",
  "🦥 {user} arrived… eventually.",
  "📟 Paging {user}… oh, they’re already here.",
  "🐢 {user} strolled in. At their pace.",
  "💀 Server now haunted by {user}.",
  "🪑 {user} sat down. Things just got weird.",
  "🎲 {user} rolled up. RNG not in your favor.",
  "💿 {user} joined. Buffering personality...",
  "🪫 {user} just joined with 2% battery.",
  "📴 {user} popped in. No signal though.",
  "🧂 {user} joined. Salty already.",
  "🌪️ {user} joined like a wind of bad choices.",
  "🐍 {user} slid in. Hiss-terical!",
  "🫥 {user}? More like background character.",
  "🤖 {user} is here. Please reboot humanity.",
  "🎤 {user} joined. Mic still muted.",
  "🧊 {user} = ice. Cold, unshaken.",
  "🛹 {user} rolled in. No brakes.",
  "🍕 {user} is here. Party confirmed.",
  "📼 {user} joined. On VHS energy.",
  "👽 {user} joined. Earth wasn’t enough.",
  "🦗 {user} joined. *Crickets*",
  "👣 {user} left footprints. And questions.",
  "🧃 {user} sipped in like a juice box.",
    
  "🚨 New player detected: {user}. Proceed with caution.",
  "📦 {user} just got delivered to the server. No returns allowed.",
  "🔔 Alert! {user} joined. Chaos level increased.",
  "💀 {user} just arrived. Server risk: 100%",
  "🧠 {user} joined with 200 IQ… or so they claim.",
  "🗿 {user} is here. The meme energy is rising.",
  "🎯 {user} just spawned. Accuracy: 0%. Confidence: 100%.",
  "🥶 {user} pulled up colder than my WiFi in winter.",
  "🐸 {user} entered. *It’s Wednesday, my dudes*.",
  "👀 {user} is watching. Be afraid. Or not.",
  "😎 {user} joined. Sunglasses indoors energy.",
  "🧂 {user} brings the salt AND the spice.",
  "🐌 {user} came in slow… but they’re here.",
    
  "🍞 {user} followed the crumbs and arrived here. They like bread.",
  "🧃 {user} brought snacks. They're cool now.",
  "🤖 {user} was built different... literally.",
  "🌈 {user} just rainbow-dashed in!",
  "🪑 {user} sat on the wrong chair and ended up here.",
  "🚀 {user} came in like a meteor. No survivors.",
  "🧀 {user} smells like victory and cheese.",
  "🍕 {user} promised free pizza. We’re watching.",
  "🦄 {user} rode in on a unicorn. Respect.",
  "🎩 {user} just did a magic trick. They're still clapping.",
  "🌟 {user} joined. Stars aligned. Server blessed.",

  "🍳 {user} broke 7 eggs and screamed 'I’m here!'",
  "🔧 {user} duct-taped the server back together. It’s worse now.",
  "🪑 {user} stacked all the chairs. Then vanished.",
  "📎 {user} brought a paperclip. Chaos followed.",
  "🔔 {user} rang a bell. We didn’t like what answered.",
  "🧨 {user} lit something. No one asked what.",
  "🚪 {user} kicked the door down. There wasn’t a door.",
  "🧃 {user} drank from the cursed juice box. Bold.",
  "🐔 {user} unleashed 100 chickens. Why? Don’t ask.",
  "🐌 {user} entered slowly… but left destruction.",
  "📦 {user} arrived in a box labeled 'do not open.' Oops.",
  "🧲 {user} magnetized everything. Including your dignity.",
  "🪄 {user} cast Yeetus Maximus. Someone flew.",
  "💫 {user} tripped on nothing and phased into reality.",
  "🦆 {user} brought ducks. There are no rules anymore.",
  "🌪️ {user} spun in, screamed, and stayed.",
  "🎉 {user} detonated the welcome confetti. It was explosive.",
  "📉 {user} crashed morale and the stock market.",
  "🔊 {user} turned the volume to 666. It echoed.",
  "🧃 {user} poured juice into the mainframe. It runs better now.",

  "💾 {user} just booted up. BIOS approved.",
  "🧠 {user} connected to the mainframe. Mind blown.",
  "⚠️ {user} caused a kernel panic. Please reboot.",
  "📡 {user} pinged the server. Server screamed.",
  "🖥️ {user} installed themselves. No admin rights needed.",
  "🔋 {user} joined with 2% battery. Risky.",
  "💻 {user} ran ‘join.exe’. It worked... somehow.",
  "📁 {user} opened a zip file. Regret followed.",
  "🖱️ {user} clicked something they shouldn’t have.",
  "🧊 {user} crashed the cloud. It’s raining bugs.",
  "📶 {user} connected on one bar. Lag incoming.",
  "🤖 {user} bypassed authentication. Very sus.",
  "🔐 {user} decrypted the welcome message. Nice.",
  "🧯 {user} started a fire in the firewall.",
  "🗑️ {user} emptied the Recycle Bin. Mistakes were made.",
  "🧱 {user} bricked a router on the way in.",
  "🔍 {user} searched 'how to join cool servers'. Found us.",
  "🪫 {user} joined, then immediately needed a recharge.",
  "🦠 {user} uploaded a virus. Now it’s a feature.",
  "📀 {user} spun up the CD-ROM. Why? Who knows.",
  "🕹️ {user} hacked reality. And then joined here.",
  "📉 {user} joined. CPU usage spiked mysteriously.",
  "🧬 {user} recompiled their DNA to fit in."
    
  "Say hi to {user}. They’re adopted. 🥹",
  "📦 {user} was found in a cardboard box and brought in.",
  "We couldn’t resist {user}’s pleading eyes. 🥺",
  "{user} expected to find silver 🪙… but found a big treasure instead. 💰",
  "{user} joined. They won’t be able to leave now. 🔒",
  "🍪 Welcome {user} in! Don’t hoard the cookies 🤨",
  "🤫 Shush! {user} joined. Let’s make a good impression. 😇",
  "📯 Hear me! {user} has stepped into the greatest of kingdoms! 🏰",
  "{user} arrived… do you think they brought snacks? 👀🍿",
  "Aye, {user} got in. Cheers, mate! 🥂",
    
  "A mysterious hat floated in… then {user} popped out. Ta-da! 🎩 🐇",
  "Who let {user} in here? Oh wait… we did. On purpose. Probably. 🤔",
  "{user} just got in. Don't scare them away. 😑",
  "{user} arrived riding a giant duck. Nobody knows why but we are keeping them. 🦆😌",
  "The new member named {user} won't share their bag of chips. 😞",
  "Act normal, {user} joined. 😰",
  "{user} opened the wrong door and now they’re stuck with us. Sorry not sorry. 😌",
  "They say chaos is a ladder. {user} climbed it sideways into the server and looks great doing it. 🪜😌",
  "Welcome the new duckling named {user} who’s too cool to quack twice. 🐣😎",
  "Watch out! {user} just dropped into the flock, and the pond’s never been the same. 🦆",
  "Wait, so {user} didn’t sign up for this? Oops. We already threw the confetti. No backing out now. 🎊",
  "Wait, they wanted a quiet place? Sorry, {user}, all we have is this beautiful chaos.🌪️",
  "Wait-{user} was hoping for normal? Too bad, this is peak weird. Glad you showed up anyway. 👀🌈 ",
  "Aye, {user} got in. Cheers, mate! 🥂"
]


class WelcomerGroup(app_commands.Group):
    def __init__(self, cog):
        super().__init__(name="welcomer", description="Manage welcome messages")
        self.cog = cog

    @app_commands.command(name="set", description="Set a channel for welcome messages")
    @app_commands.checks.has_permissions(administrator=True)
    async def set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.cog.config[str(interaction.guild.id)] = str(channel.id)
        self.cog.save_config()
        await interaction.response.send_message(
            f"<:ap_checkmark:1382760062728273920> Welcome channel set to {channel.mention}", ephemeral=True
        )

    @app_commands.command(name="test", description="Send a test welcome message")
    @app_commands.checks.has_permissions(administrator=True)
    async def test(self, interaction: discord.Interaction):
        channel_id = self.cog.config.get(str(interaction.guild.id))
        if not channel_id:
            await interaction.response.send_message(
                "<:ap_crossmark:1382760353904988230> No welcome channel is set.", ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(int(channel_id))
        if not channel:
            await interaction.response.send_message(
                "<:ap_crossmark:1382760353904988230> The configured channel was not found.", ephemeral=True
            )
            return

        msg_text = random.choice(WELCOME_MESSAGES).replace("{user}", interaction.user.mention)
        await channel.send(msg_text)
        await interaction.response.send_message("<:ap_checkmark:1382760062728273920> Test message sent.", ephemeral=True)

    @app_commands.command(name="remove", description="Remove the welcome channel setting")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction):
        if str(interaction.guild.id) in self.cog.config:
            del self.cog.config[str(interaction.guild.id)]
            self.cog.save_config()
            await interaction.response.send_message("<:ap_crossmark:1382760353904988230> Welcome channel removed.", ephemeral=True)
        else:
            await interaction.response.send_message("<:ap_crossmark:1382760353904988230> No welcome channel was set.", ephemeral=True)


class RandomWelcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.bot.tree.add_command(WelcomerGroup(self))  # Register group with subcommands

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = self.config.get(str(member.guild.id))
        if not channel_id:
            return
        channel = member.guild.get_channel(int(channel_id))
        if channel:
            msg_text = random.choice(WELCOME_MESSAGES).replace("{user}", member.mention)
            try:
                await channel.send(msg_text)
            except discord.Forbidden:
                try:
                    await channel.send(
                        f"<:ap_crossmark:1382760353904988230> I don’t have permission to send messages here! "
                        f"Please enable **Send Messages** for my role in {channel.mention}."
                    )
                except discord.Forbidden:
                    LOG_CHANNEL_ID = 1382382467184328704  # replace with your log channel ID
                    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
                    if log_channel:
                        await log_channel.send(
                        f"⚠️ I couldn’t send welcome messages in {channel.mention} "
                        f"for **{member.guild.name}** (`{member.guild.id}`) (Missing Permissions)."
                        )
            except discord.HTTPException as e:
                print(f"[Welcomer] Failed to send welcome message in {channel}: {e}")


async def setup(bot):
    await bot.add_cog(RandomWelcome(bot))
