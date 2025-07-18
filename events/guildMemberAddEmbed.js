const { Events, EmbedBuilder } = require('discord.js');

const welcomeChannelId = '1096432513834045441'; // Replace this with your welcome channel ID

module.exports = {
  name: Events.GuildMemberAdd,
  once: false,

  execute(member) {
    const channel = member.guild.channels.cache.get(welcomeChannelId);
    if (!channel) return;

    const welcomeEmbed = new EmbedBuilder()
      .setTitle(`Welcome to BMTG ↬ ᴅᴀɴᴋ・ᴏᴡᴏ・ɢɪᴠᴇᴀᴡᴀʏs・ᴇᴠᴇɴᴛs | AURA!`) // ✅ Mention in title
      .setDescription(`### Hey <@${member.id}>\n
- Check out my YouTube Videos <:bmtg_Subscribe:1096508185365450842> on ⁠https://discord.com/channels/1063458575667699832/1064194064934764606
- Grab your desired roles and more from <id:customize> and https://discord.com/channels/1063458575667699832/1309214562213691443, you can change them anytime!
- Make sure to check out https://discord.com/channels/1063458575667699832/1105157414992478268\n
Thanks for joining <:bmtg_ty_thankyou:1217690109701525524>
We hope you enjoy your stay.`)
      .setColor('#00ffe5')
      .setAuthor({
        name: member.user.tag,
        iconURL: member.user.displayAvatarURL({ dynamic: true }),
      }) // ✅ Author section with username + PFP
      .setThumbnail(member.guild.iconURL({ dynamic: true })) // ✅ Server icon as thumbnail
      .setFooter({ text: `You are our ${member.guild.memberCount} member!` })
      .setTimestamp();

    channel.send({ embeds: [welcomeEmbed] }).catch(console.error);
  },
};
