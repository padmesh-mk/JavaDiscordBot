const { SlashCommandBuilder } = require('@discordjs/builders');
const { EmbedBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('ping')
        .setDescription('Checks the bot latency.'),
    
    async execute(interaction) {
        // Calculate latency
        const ping = Date.now() - interaction.createdTimestamp;
        const apiPing = interaction.client.ws.ping;

        // Create an embed for the response
        const embed = new EmbedBuilder()
            .setColor('#00c0ff') // Green color
            .setTitle('🏓 Pong!')
            .setDescription(
                `**Bot Latency:** ${ping}ms\n` +
                `**API Latency:** ${apiPing}ms`
            )
            .setTimestamp();

        // Send the response as an embed
        await interaction.reply({ embeds: [embed] });
    },
};
