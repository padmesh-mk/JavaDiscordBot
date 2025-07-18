const { EmbedBuilder } = require('discord.js');

module.exports = {
  name: 'membercount',
  description: 'Shows the current member count of the server, including bots and humans',
  execute(message) {
    const total = message.guild.memberCount;
    const bots = message.guild.members.cache.filter(member => member.user.bot).size;
    const humans = total - bots;

    const embed = new EmbedBuilder()
      .setTitle('📊 Guild Members')
      .setDescription(
        `There are **${total}** members in this guild.\n` +
        `🧑 Real Members: **${humans}**\n🤖 Bots: **${bots}**`
      )
      .setColor('#00ffe5')
      .setTimestamp();

    message.channel.send({ embeds: [embed] });
  },
};
