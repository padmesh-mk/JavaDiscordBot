const { EmbedBuilder } = require('discord.js'); // Correct import for discord.js v14

module.exports = {
    name: 'ping', // Command name for prefix
    description: 'Checks the bot latency.',
    cooldown: 5, // Optional cooldown to prevent spamming
    
    async execute(message, args) {
        // Calculate latency
        const ping = Date.now() - message.createdTimestamp;
        const apiPing = message.client.ws.ping;

        // Create an embed for the response
        const embed = new EmbedBuilder()
            .setColor('#00c0ff') // Set the color for the embed
            .setTitle('🏓 Pong!')
            .setDescription(
                `**Bot Latency:** ${ping}ms\n` +
                `**API Latency:** ${apiPing}ms`
            )
            .setTimestamp();

        // Send the response as an embed
        await message.channel.send({ embeds: [embed] });

        // Optionally delete the command message to avoid clutter
        if (message.deletable) {
            await message.delete();
        }
    },
};
