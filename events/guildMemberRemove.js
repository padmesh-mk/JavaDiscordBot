const { Events, EmbedBuilder } = require('discord.js');

const leaveChannelId = '1270059585448837202'; // Replace with your actual leave log channel ID

module.exports = {
  name: Events.GuildMemberRemove,
  once: false,

  execute(member) {
    const channel = member.guild.channels.cache.get(leaveChannelId);
    if (!channel) return;

    const leaveEmbed = new EmbedBuilder()
      .setDescription(`Unfortunately, <@${member.id}> has left **BMTG ↬ ᴅᴀɴᴋ・ᴏᴡᴏ・ɢɪᴠᴇᴀᴡᴀʏs・ᴇᴠᴇɴᴛs | AURA!**`)
      .setColor('#ff0000')
      .setAuthor({
        name: member.user.tag,
        iconURL: member.user.displayAvatarURL({ dynamic: true }),
      })
      .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
      .setFooter({ text: `We now have ${member.guild.memberCount} members.` })
      .setTimestamp();

    channel.send({ embeds: [leaveEmbed] }).catch(console.error);
  },
};
