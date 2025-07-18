const { Events } = require('discord.js');

const OWO_BOT_ID = '408785106942164992';
const TARGET_CHANNEL_ID = '1285096477059977288'; // 🔁 Replace this with the channel ID

module.exports = {
  name: Events.MessageCreate,

  async execute(message) {
    if (
      message.channel.id !== TARGET_CHANNEL_ID ||
      message.author?.id !== OWO_BOT_ID ||
      !message.embeds?.length
    ) return;

    const embed = message.embeds[0];
    const authorName = embed.author?.name || '';

    if (!authorName.includes('HuntBot')) return;

    const channel = message.channel;

    // 🕵️ Get the user message before the OwO message
    const fetched = await channel.messages.fetch({ limit: 2 });
    const userMsg = fetched.find(m => m.id !== message.id && m.author.id !== OWO_BOT_ID);

    // 📩 Reply with countdown message
    const replyMsg = await channel.send({
      content: `Claim only when your **HuntBot is ready**!\nDeletes in:`
    });

    const countdown = ['5️⃣', '4️⃣', '3️⃣', '2️⃣', '1️⃣'];
    for (const emoji of countdown) {
      await replyMsg.react(emoji).catch(() => {});
      await new Promise(res => setTimeout(res, 1000));
    }

    // 🗑️ Delete messages after countdown
    setTimeout(async () => {
      if (userMsg) await userMsg.delete().catch(() => {});
      await message.delete().catch(() => {});
      await replyMsg.delete().catch(() => {});
    }, 500);
  }
};
