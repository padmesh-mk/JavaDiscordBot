const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const fs = require('fs');

// Path to cookie file
const cookieFile = './cookie.json';

// Whitelisted user IDs
const ALLOWED_USERS = ['941902212303556618', '118507834299252752'];

// Channel where logs are sent
const LOG_CHANNEL_ID = '1389541095360168028'; // 🔁 Replace with actual channel ID

module.exports = {
  data: new SlashCommandBuilder()
    .setName('cookiedel')
    .setDescription('Delete a user entry from cookie.json')
    .addStringOption(option =>
      option.setName('userid')
        .setDescription('Enter the user ID to delete')
        .setRequired(true)
    ),

  async execute(interaction) {
    if (!ALLOWED_USERS.includes(interaction.user.id)) {
      return interaction.reply({ content: 'You are not allowed to use this command.', ephemeral: true });
    }

    const userId = interaction.options.getString('userid');

    if (!fs.existsSync(cookieFile)) fs.writeFileSync(cookieFile, '{}');
    const cookies = JSON.parse(fs.readFileSync(cookieFile));

    if (cookies[userId]) {
      const removedAmount = cookies[userId].amount;
      delete cookies[userId];
      fs.writeFileSync(cookieFile, JSON.stringify(cookies, null, 2));

      await interaction.reply({ content: `✅ Deleted.`, ephemeral: true });

      // Send log
      const logChannel = interaction.client.channels.cache.get(LOG_CHANNEL_ID);
      if (logChannel) {
        const logEmbed = new EmbedBuilder()
          .setTitle('🍪 Cookie Entry Deleted')
          .addFields(
            { name: 'User ID', value: userId, inline: true },
            { name: 'Amount Removed', value: removedAmount.toString(), inline: true },
            { name: 'Deleted By', value: `<@${interaction.user.id}>`, inline: false }
          )
          .setColor(0xff5555)
          .setTimestamp();

        logChannel.send({ embeds: [logEmbed] }).catch(console.error);
      }

    } else {
      await interaction.reply({ content: '❌ No user found.', ephemeral: true });
    }
  }
};
