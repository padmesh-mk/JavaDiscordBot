const { SlashCommandBuilder, EmbedBuilder, PermissionsBitField } = require('discord.js');
const fs = require('fs');
const donationFile = './donations.json';

function loadDonations() {
  if (!fs.existsSync(donationFile)) fs.writeFileSync(donationFile, '{}');
  return JSON.parse(fs.readFileSync(donationFile));
}

function saveDonations(data) {
  fs.writeFileSync(donationFile, JSON.stringify(data, null, 2));
}

module.exports = {
  data: new SlashCommandBuilder()
    .setName('owo')
    .setDescription('Manage and view OwO donations')
    .addSubcommandGroup(group =>
      group.setName('dono')
        .setDescription('OwO Donation Tools')
        .addSubcommand(sub =>
          sub.setName('add')
            .setDescription('Manually add a donation')
            .addUserOption(opt =>
              opt.setName('user').setDescription('User who donated').setRequired(true))
            .addIntegerOption(opt =>
              opt.setName('amount').setDescription('Amount donated').setRequired(true)))
        .addSubcommand(sub =>
          sub.setName('remove')
            .setDescription('Remove a donation amount from a user')
            .addUserOption(opt =>
              opt.setName('user').setDescription('User to remove donation from').setRequired(true))
            .addIntegerOption(opt =>
              opt.setName('amount').setDescription('Amount to remove').setRequired(true)))
        .addSubcommand(sub =>
          sub.setName('check')
            .setDescription('Check total donations by a user')
            .addUserOption(opt =>
              opt.setName('user').setDescription('User to check').setRequired(true)))
        .addSubcommand(sub =>
          sub.setName('lb').setDescription('Show top 10 donation leaderboard'))),

  async execute(interaction) {
    const sub = interaction.options.getSubcommand();
    const donations = loadDonations();
    const logChannelId = '1381822531681517629';

    await interaction.deferReply({ ephemeral: false });

    // ADD
    if (sub === 'add') {
      if (!interaction.member.permissions.has(PermissionsBitField.Flags.Administrator)) {
        return await interaction.editReply({
          content: '❌ You do not have permission to use this command.',
          ephemeral: true
        });
      }

      const user = interaction.options.getUser('user');
      const amount = interaction.options.getInteger('amount');

      donations[user.id] = (donations[user.id] || 0) + amount;
      saveDonations(donations);

      const replyEmbed = new EmbedBuilder()
        .setAuthor({ name: `${user.username}'s OwO Donation`, iconURL: user.displayAvatarURL() })
        .setColor(0x2ECC71)
        .addFields(
          { name: 'Your Donation', value: `• \`${amount.toLocaleString()}\`` },
          { name: 'Summary', value: `• **Amount added:** \`${amount.toLocaleString()}\`\n• **Total donated:** \`${donations[user.id].toLocaleString()}\`` }
        )
        .setFooter({ text: 'Thanks for Donating <3' });

      const logEmbed = new EmbedBuilder()
        .setAuthor({ name: `${user.username}'s OwO Donation`, iconURL: user.displayAvatarURL() })
        .setColor(0x00AE86)
        .addFields(
          { name: 'New Donation', value: `• **Amount added:** \`${amount.toLocaleString()}\`\n• **Total donated:** \`${donations[user.id].toLocaleString()}\`` },
          { name: 'Manually Added By:', value: `<@${interaction.user.id}> in <#${interaction.channel.id}>` }
        );

      await interaction.editReply({ embeds: [replyEmbed] });

      const logChannel = interaction.guild.channels.cache.get(logChannelId);
      if (logChannel) await logChannel.send({ embeds: [logEmbed] });
    }

    // REMOVE
    else if (sub === 'remove') {
      if (!interaction.member.permissions.has(PermissionsBitField.Flags.Administrator)) {
        return await interaction.editReply({
          content: '❌ You do not have permission to use this command.',
          ephemeral: true
        });
      }

      const user = interaction.options.getUser('user');
      const amount = interaction.options.getInteger('amount');
      const current = donations[user.id] || 0;

      if (amount > current) {
        return await interaction.editReply({
          content: `❌ Cannot remove \`${amount.toLocaleString()}\` from <@${user.id}>. They only have \`${current.toLocaleString()}\` donated.`,
          ephemeral: true
        });
      }

      donations[user.id] = current - amount;
      if (donations[user.id] <= 0) delete donations[user.id];
      saveDonations(donations);

      const replyEmbed = new EmbedBuilder()
        .setAuthor({ name: `${user.username}'s OwO Donation`, iconURL: user.displayAvatarURL() })
        .setColor(0xE74C3C)
        .addFields(
          { name: 'Donation Removed', value: `• \`${amount.toLocaleString()}\`` },
          { name: 'Summary', value: `• **Amount removed:** \`${amount.toLocaleString()}\`\n• **Remaining total:** \`${(donations[user.id] || 0).toLocaleString()}\`` }
        )
        .setFooter({ text: 'Donation adjusted manually.' });

      const logEmbed = new EmbedBuilder()
        .setAuthor({ name: `${user.username}'s OwO Donation`, iconURL: user.displayAvatarURL() })
        .setColor(0xC0392B)
        .addFields(
          { name: 'Donation Removed', value: `• **Amount removed:** \`${amount.toLocaleString()}\`\n• **Remaining total:** \`${(donations[user.id] || 0).toLocaleString()}\`` },
          { name: 'Removed By:', value: `<@${interaction.user.id}> in <#${interaction.channel.id}>` }
        );

      await interaction.editReply({ embeds: [replyEmbed] });

      const logChannel = interaction.guild.channels.cache.get(logChannelId);
      if (logChannel) await logChannel.send({ embeds: [logEmbed] });
    }

    // CHECK
    else if (sub === 'check') {
      const user = interaction.options.getUser('user');
      const total = donations[user.id] || 0;

      const embed = new EmbedBuilder()
        .setAuthor({ name: `${user.tag} (${user.id})`, iconURL: user.displayAvatarURL() })
        .addFields({ name: 'Total Donations:', value: `\`${total.toLocaleString()}\`` })
        .setColor(0xCCCCFF);

      await interaction.editReply({ embeds: [embed] });
    }

    // LEADERBOARD
    else if (sub === 'lb') {
      const sorted = Object.entries(donations).sort(([, a], [, b]) => b - a);
      const perPage = 10;
      const totalPages = Math.ceil(sorted.length / perPage);
      let page = 0;

      const generateEmbed = async (pageNum) => {
        const start = pageNum * perPage;
        const current = sorted.slice(start, start + perPage);
        const description = await Promise.all(current.map(async ([id, amount], index) => {
          const user = await interaction.client.users.fetch(id).catch(() => null);
          const pos = start + index + 1;
          const medal = pos === 1 ? '🥇' : pos === 2 ? '🥈' : pos === 3 ? '🥉' : '🔹';
          return `${medal} \` ${amount.toLocaleString()} \` - ${user ? user.username : `Unknown (${id})`}`;
        }));

        return new EmbedBuilder()
          .setTitle('OwO Donation Leaderboard')
          .addFields(
            { name: 'Total Donators:', value: `${Object.keys(donations).length}`, inline: true },
            { name: 'Total Donations:', value: `${Object.values(donations).reduce((a, b) => a + b, 0).toLocaleString()}`, inline: true }
          )
          .setDescription(description.join('\n') || 'No donations yet.')
          .setFooter({ text: `Page ${pageNum + 1} of ${totalPages}` })
          .setColor(0x9B59B6);
      };

      const row = {
        type: 1,
        components: [
          { type: 2, style: 2, label: '◀️', custom_id: 'prev_lb' },
          { type: 2, style: 2, label: '▶️', custom_id: 'next_lb' }
        ]
      };

      const msg = await interaction.editReply({
        embeds: [await generateEmbed(page)],
        components: [row]
      });

      const collector = msg.createMessageComponentCollector({ time: 60000 });

      collector.on('collect', async i => {
        if (i.user.id !== interaction.user.id) {
          return i.reply({ content: 'Only you can interact with this leaderboard.', ephemeral: true });
        }

        if (i.customId === 'prev_lb') page = page > 0 ? page - 1 : totalPages - 1;
        if (i.customId === 'next_lb') page = page < totalPages - 1 ? page + 1 : 0;

        await i.update({
          embeds: [await generateEmbed(page)],
          components: [row]
        });
      });

      collector.on('end', async () => {
        if (msg.editable) await msg.edit({ components: [] });
      });
    }
  }
};
