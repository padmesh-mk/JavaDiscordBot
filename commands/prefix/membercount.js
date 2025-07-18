const { EmbedBuilder } = require('discord.js');

module.exports = {
  name: 'membercount',
  aliases: ['mc'], // Support for both 'membercount' and 'mc'
  description: 'Shows the current member count of the server, including bots and real members',
  async execute(message) {
    await message.guild.members.fetch();

    const totalMembers = message.guild.memberCount;
    const bots = message.guild.members.cache.filter(member => member.user.bot).size;
    const realMembers = totalMembers - bots;

    const embed = new EmbedBuilder()
      .setTitle('📊 Guild Members')
      .setDescription(
        `There are **${totalMembers}** members in this guild.\n` +
        `🧑 Real Members: **${realMembers}**\n🤖 Bots: **${bots}**`
      )
      .setColor('#00ffe5')
      .setTimestamp();

    message.channel.send({ embeds: [embed] });
  },
};
