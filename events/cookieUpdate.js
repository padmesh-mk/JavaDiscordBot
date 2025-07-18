const { EmbedBuilder } = require('discord.js');
const fs = require('fs');

// Constants
const cookieFile = './cookie.json';
const PAYOUT_CHANNEL_ID = '1386611173717446747';
const OWO_BOT_ID = '408785106942164992';
const LOG_CHANNEL_ID = '1389541095360168028'; // 🔁 Replace with your actual log channel ID

function loadCookies() {
  if (!fs.existsSync(cookieFile)) fs.writeFileSync(cookieFile, '{}');
  return JSON.parse(fs.readFileSync(cookieFile));
}

function saveCookies(data) {
  fs.writeFileSync(cookieFile, JSON.stringify(data, null, 2));
}

module.exports = {
  name: 'messageUpdate',
  async execute(oldMessage, newMessage) {
    if (
      newMessage.channel.id !== PAYOUT_CHANNEL_ID ||
      newMessage.author?.id !== OWO_BOT_ID ||
      !newMessage.content.includes('cowoncy')
    ) return;

    const cookies = loadCookies();

    const match = newMessage.content.match(/to \*\*<@!?(\d+)>/);
    const receiverId = match?.[1];

    if (!receiverId || !cookies[receiverId]) return;

    const removedAmount = cookies[receiverId].amount;
    delete cookies[receiverId];
    saveCookies(cookies);

    await newMessage.react('💰');

    // Create message link
    const messageLink = `https://discord.com/channels/${newMessage.guild.id}/${newMessage.channel.id}/${newMessage.id}`;

    // Logging
    const logChannel = newMessage.guild.channels.cache.get(LOG_CHANNEL_ID);
    if (logChannel) {
      const logEmbed = new EmbedBuilder()
        .setTitle('💸 Cookie Entry Paid Out')
        .addFields(
          { name: 'User', value: `<@${receiverId}> (${receiverId})`, inline: true },
          { name: 'Amount Removed', value: removedAmount.toString(), inline: true },
          { name: 'Message Link', value: `[Jump to Message](${messageLink})`, inline: false },
          { name: 'Triggered By', value: 'OwO Bot (Auto Detected)' }
        )
        .setColor(0xe17055)
        .setTimestamp();

      logChannel.send({ embeds: [logEmbed] }).catch(console.error);
    }
  }
};
