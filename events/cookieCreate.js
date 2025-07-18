const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const fs = require('fs');

// File and channel constants
const cookieFile = './cookie.json';
const COOKIE_CHANNEL_ID = '1386610908805075005';
const PAYOUT_CHANNEL_ID = '1386611173717446747';
const TARGET_RECEIVER_ID = '118507834299252752';
const OWO_BOT_ID = '408785106942164992';
const LOG_CHANNEL_ID = '1389541445777752084'; // Replace with your actual log channel ID

function loadCookies() {
  if (!fs.existsSync(cookieFile)) fs.writeFileSync(cookieFile, '{}');
  return JSON.parse(fs.readFileSync(cookieFile));
}

function saveCookies(data) {
  fs.writeFileSync(cookieFile, JSON.stringify(data, null, 2));
}

module.exports = {
  name: 'messageCreate',
  async execute(message) {
    if (!message.guild) return;

    const content = message.content;
    const cookies = loadCookies();

    // Cookie received logic
    if (
      message.channel.id === COOKIE_CHANNEL_ID &&
      message.author.id === OWO_BOT_ID &&
      content.includes('cookieeat') &&
      content.includes(`<@${TARGET_RECEIVER_ID}>`)
    ) {
      const giverMatch = content.match(/from \*\*<@!?(\d+)>/);
      const giverId = giverMatch?.[1];
      if (!giverId) return;

      cookies[giverId] = cookies[giverId] || { amount: 0 };
      cookies[giverId].amount += 50000;
      saveCookies(cookies);

      await message.react('🍪');

      // Message link
      const messageLink = `https://discord.com/channels/${message.guild.id}/${message.channel.id}/${message.id}`;

      // Logging to log channel
      const logChannel = message.guild.channels.cache.get(LOG_CHANNEL_ID);
      if (logChannel) {
        const logEmbed = new EmbedBuilder()
          .setTitle('🍪 Cookie Sent')
          .addFields(
            { name: 'Giver', value: `<@${giverId}> (${giverId})`, inline: true },
            { name: 'Receiver', value: `<@${TARGET_RECEIVER_ID}> (${TARGET_RECEIVER_ID})`, inline: true },
            { name: 'Total Cookies', value: cookies[giverId].amount.toString(), inline: true },
            { name: 'Message Link', value: `[Jump to Message](${messageLink})`, inline: false }
          )
          .setTimestamp()
          .setColor(0x00b894);

        logChannel.send({ embeds: [logEmbed] }).catch(console.error);
      }

      return;
    }

    // Payout list logic
    if (
      message.channel.id === PAYOUT_CHANNEL_ID &&
      /\bcookie\b/i.test(content)
    ) {
      const entries = Object.entries(cookies);
      if (entries.length === 0) {
        return message.reply({
          content: 'No cookies being tracked.',
          allowedMentions: { repliedUser: false }
        });
      }

      const perPage = 5;
      let page = 0;
      const totalPages = Math.ceil(entries.length / perPage);

      const generateEmbed = (page) => {
        const list = entries
          .slice(page * perPage, (page + 1) * perPage)
          .map(([id, data]) => `\`\`\`wgive <@${id}> ${data.amount}\`\`\``)
          .join('\n');

        return new EmbedBuilder()
          .setTitle('🍪 TDE Cookie List')
          .setDescription(list)
          .setColor(0xffc107)
          .setFooter({ text: `Page ${page + 1} of ${totalPages}` });
      };

      const row = new ActionRowBuilder().addComponents(
        new ButtonBuilder()
          .setCustomId('prev_cookie_page')
          .setLabel('◀️')
          .setStyle(ButtonStyle.Secondary),
        new ButtonBuilder()
          .setCustomId('next_cookie_page')
          .setLabel('▶️')
          .setStyle(ButtonStyle.Secondary)
      );

      const reply = await message.reply({
        embeds: [generateEmbed(page)],
        components: [row],
        allowedMentions: { repliedUser: false }
      });

      const collector = reply.createMessageComponentCollector({ time: 60000 });

      collector.on('collect', async (i) => {
        if (i.user.id !== message.author.id) {
          return i.reply({ content: 'Only you can navigate this.', ephemeral: true });
        }

        if (i.customId === 'prev_cookie_page') page = (page - 1 + totalPages) % totalPages;
        if (i.customId === 'next_cookie_page') page = (page + 1) % totalPages;

        await i.update({ embeds: [generateEmbed(page)], components: [row] });
      });

      collector.on('end', () => {
        if (reply.editable) reply.edit({ components: [] }).catch(() => {});
      });
    }
  }
};
