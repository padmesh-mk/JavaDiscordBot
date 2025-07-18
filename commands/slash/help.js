const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('help')
        .setDescription('Displays a help menu with information about commands.'),

    async execute(interaction) {
        // Total number of pages in the help menu
        const totalPages = 4;

        // Create embed for the first page
        const getEmbedForPage = (page) => {
            const embed = new EmbedBuilder().setColor('#00c0ff').setTimestamp();

            if (page === 1) {
                embed
                    .setTitle('Help Menu - General Slash Commands')
                    .setDescription(
                        '</help:1317454985801502803>\n' +
                    	'⤷ Displays this help menu\n' +
                        '</ping:1317454985801502804>\n' +
                    	'⤷ Check if the bot is online' +
                        '</owo dono check:1387129068612227165>\n' +
                    	'⤷ To check an user OwO Donations\n' +
                        '</owo dono lb:1387129068612227165>\n' +
                    	'⤷ To display top 10 OwO Donations\n'                   
                    )
                    .setFooter({ text: 'Page 1 of 4' });
            } else if (page === 2) {
                embed
                    .setTitle('Help Menu - General Prefix Commands')
                    .setDescription(
                        '`&ping`\n' +
                    	'⤷ Check if the bot is online\n' +
                        '`&uptime`\n' +
                    	'⤷ Check the uptime of bot\n' +
                    	'`&membercount | &mc`\n' +
                    	'⤷ Check the Guild Member Count\n' +
                        '`&rem`\n' +
                    	'⤷ Daily reminder for few bots'
                    )
                    .setFooter({ text: 'Page 2 of 4' });
            } else if (page === 3) {
                embed
                    .setTitle('Help Menu - Perks Prefix Commands')
                    .setDescription(
                        '`&kik [user][reason]`\n' +
                        '⤷ Fake kick an user\n' +
                        '`&bon [user][reason]`\n' +
                        '⤷ Fake ban an user'
                    )
                    .setFooter({ text: 'Page 3 of 4' });
            } else if (page === 4) {
                embed
                    .setTitle('Help Menu - Admin Commands')
                    .setDescription(
                        '`&bat [message]`\n' +
                        '⤷ Staff battle ping'
                    )
                    .setFooter({ text: 'Page 4 of 4' });
            }

            return embed;
        };

        // Create navigation buttons
        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('first')
                    .setLabel('⏮️ First')
                    .setStyle(ButtonStyle.Primary),

                new ButtonBuilder()
                    .setCustomId('back')
                    .setLabel('⬅️ Back')
                    .setStyle(ButtonStyle.Secondary),

                new ButtonBuilder()
                    .setCustomId('forward')
                    .setLabel('➡️ Forward')
                    .setStyle(ButtonStyle.Secondary),

                new ButtonBuilder()
                    .setCustomId('last')
                    .setLabel('⏭️ Last')
                    .setStyle(ButtonStyle.Primary)
            );

        let currentPage = 1; // Starting page

        // Send the first page
        await interaction.reply({ embeds: [getEmbedForPage(currentPage)], components: [row], ephemeral: false });

        // Collect button interactions
        const filter = (i) => i.user.id === interaction.user.id;
        const collector = interaction.channel.createMessageComponentCollector({ filter, time: 60000 }); // 1-minute collector

        collector.on('collect', async (i) => {
            if (i.customId === 'first') currentPage = 1;
            if (i.customId === 'back' && currentPage > 1) currentPage--;
            if (i.customId === 'forward' && currentPage < totalPages) currentPage++;
            if (i.customId === 'last') currentPage = totalPages;

            // Update the embed for the new page
            await i.update({ embeds: [getEmbedForPage(currentPage)], components: [row] });
        });

        collector.on('end', () => {
            // Disable buttons after the collector ends
            row.components.forEach((button) => button.setDisabled(true));
            interaction.editReply({ components: [row] }).catch(console.error);
        });
    },
};
