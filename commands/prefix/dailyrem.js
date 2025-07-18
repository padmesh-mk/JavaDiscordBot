const { EmbedBuilder } = require('discord.js'); // Correct import for discord.js v14

module.exports = {
    name: 'rem',
    description: 'Daily Reminder.',
    cooldown: 5, // 24 hours cooldown in seconds
    execute(message, args) {
        // Create the embed
        const embed = new EmbedBuilder()
            .setColor('#00c0ff') // Fixed method to set the embed color
            .setTitle('Daily Reminder')
            .setDescription(
                '**Dank Memer:** \n' +
                '- Daily: </daily:1011560370864930856> \n' +
                '- Work: </work shift:1011560371267579942> \n' +
                '- Pets: </pets care:1011560371171102768> \n' +     
                '- Scratch: </scratch:1011560371267579934> \n' +
                '- Stream: </stream:1011560371267579938> \n' +
                '- Weekly: </weekly:1011560370948800549> \n' +
                '- Monthly: </monthly:1011560370911072262> \n\n' +
                '**Rumble Royale:** \n' +
                '- Daily: </daily:975902717002285127> \n' +
                '- Quests: </quests:1363578092911595732> \n' +
                '- Weekly: </weekly:975902718570942464> \n\n' +
                '**Others:** \n' +
				'- Ghostly: `?daily` | `?weekly` \n' +
                '- Mafia: </daily:1024791190941466677> \n\n' +
				'**Vote Links:** \n' +
                '- Dank Vote: </vote:1011560370994954286> \n' +
                '- Rumble Vote: </vote:974436177115484230> \n' +
                '- [OwO vote](https://top.gg/bot/408785106942164992/vote) \n' +
                '- [Reaction bot vote](https://top.gg/bot/519287796549156864/vote) \n' +
                '- [AuraPrime vote](https://top.gg/bot/1316827072655523911/vote) \n'
            )
            .setFooter({ 
                text: 'BMTG | AURA', 
                iconURL: 'https://cdn.discordapp.com/icons/1063458575667699832/a_00030a2bbe60e06071ad5b259360ea53.gif?size=1024&width=640&height=640' 
            }) // Optional icon
            .setTimestamp();

        // Send the embed
        message.channel.send({ embeds: [embed] });
    },
};
