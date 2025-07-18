const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'uptime',
    description: 'Shows the bot\'s uptime.',
    execute(message, args) {
        // Get the bot's uptime (in milliseconds)
        const uptime = message.client.uptime;

        // Calculate the days, hours, minutes, and seconds
        const days = Math.floor(uptime / (1000 * 60 * 60 * 24));
        const hours = Math.floor((uptime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((uptime % (1000 * 60)) / 1000);

        // Format uptime message
        const uptimeMessage = `${days}d ${hours}h ${minutes}m ${seconds}s`;

        // Create the embed with the uptime info
        const embed = new EmbedBuilder()
            .setColor('#00ffe5')
            .setTitle('Bot Uptime')
            .setDescription(`The bot has been online for: **${uptimeMessage}**`)
            .setFooter({ text: 'Uptime info', iconURL: 'https://cdn.discordapp.com/icons/1063458575667699832/a_00030a2bbe60e06071ad5b259360ea53.gif?size=1024&width=640&height=640' })
            .setTimestamp();

        // Send the embed to the channel
        message.channel.send({ embeds: [embed] });
    },
};
