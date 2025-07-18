const fs = require('fs');
const { EmbedBuilder } = require('discord.js');

const watchedChannelIds = [
  '1309391051068276776',
  '1309395345179938865',
  '1314472110038712391',
  '1354518893154140170'
];
const yourUserId = '941902212303556618';
const logChannelId = '1381822531681517629';
const donationFile = './donations.json';

function loadDonations() {
  if (!fs.existsSync(donationFile)) fs.writeFileSync(donationFile, '{}');
  return JSON.parse(fs.readFileSync(donationFile));
}

function saveDonations(data) {
  fs.writeFileSync(donationFile, JSON.stringify(data, null, 2));
}

module.exports = {
  name: 'messageUpdate',
  async execute(oldMsg, newMsg) {
    try {
      if (!watchedChannelIds.includes(newMsg.channelId)) return;
      if (!newMsg.author?.bot || !newMsg.content.includes('cowoncy')) return;

      // ✅ Prevent re-processing if message content hasn't changed
      if (oldMsg.content === newMsg.content) return;

      const parts = newMsg.content.split(' ');
      if (parts.length < 8) return;

      const donorId = parts[2].split('<@')[1]?.split('>')[0];
      if (!donorId) return;

      const amountStr = parts[4].replace('**', '').replace(/,/g, '');
      const amount = parseInt(amountStr, 10);
      if (isNaN(amount)) return;

      const recipientId = parts[7].split('<@')[1]?.split('>')[0]?.replace('**!', '');
      if (recipientId !== yourUserId) return;

      const donations = loadDonations();
      donations[donorId] = (donations[donorId] || 0) + amount;
      saveDonations(donations);

      const donorUser = await newMsg.client.users.fetch(donorId).catch(() => null);
      const logChannel = newMsg.guild.channels.cache.get(logChannelId);

      if (!donorUser || !logChannel) return;

      // ✅ Reply Embed (User View)
      const replyEmbed = new EmbedBuilder()
        .setAuthor({ name: `${donorUser.username}'s OwO Donation`, iconURL: donorUser.displayAvatarURL() })
        .setColor(0x2ECC71)
        .addFields(
          { name: 'Your Donation', value: `• \`${amount.toLocaleString()}\`` },
          {
            name: 'Summary',
            value: `• **Amount added:** \`${amount.toLocaleString()}\`\n• **Total donated:** \`${donations[donorId].toLocaleString()}\``
          }
        )
        .setFooter({ text: 'Thanks for Donating <3' });

      // 📋 Log Embed (Admin Log)
      const logEmbed = new EmbedBuilder()
        .setAuthor({ name: `${donorUser.username}'s OwO Donation`, iconURL: donorUser.displayAvatarURL() })
        .setColor(0x00AE86)
        .addFields(
          {
            name: 'New Donation',
            value: `• **Amount added:** \`${amount.toLocaleString()}\`\n• **Total donated:** \`${donations[donorId].toLocaleString()}\``
          },
          {
            name: 'Donated In:',
            value: `<#${newMsg.channel.id}>`
          }
        );

      await newMsg.react('✅');
      await newMsg.reply({ embeds: [replyEmbed] });
      await logChannel.send({ embeds: [logEmbed] });

    } catch (err) {
      console.error('❌ Donation Logger Error:', err.message);
    }
  }
};
