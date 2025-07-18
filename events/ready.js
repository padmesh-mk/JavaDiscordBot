const { REST, Routes, ActivityType } = require('discord.js');
const fs = require('fs');
const cron = require('node-cron');
require('dotenv').config();

// Reminder Channel & Role Config
const CHANNEL_ID_1 = '1386610908805075005';
const ROLE_ID_1 = '1362703328878002389';
const MESSAGE_1 = `Hey <@&${ROLE_ID_1}>! Don't forget to send your cookie to kaisertde 🍪`;

const CHANNEL_ID_2 = '1356194205701116075';
const ROLE_ID_2 = '1360858589866233957';
const MESSAGE_2 = `Hey <@&${ROLE_ID_2}>! Time to send Clover to Padmesh 🍀`;

module.exports = {
    name: 'ready',
    once: true,
    async execute(client) {
        console.log(`🤖 Logged in as ${client.user.tag}`);

        // Slash command registration
        const guildIds = client.guilds.cache.map(guild => guild.id);
        const commands = [];
        const commandFiles = fs.readdirSync('./commands/slash').filter(file => file.endsWith('.js'));

        for (const file of commandFiles) {
            const command = require(`../commands/slash/${file}`);
            commands.push(command.data.toJSON());
        }

        const rest = new REST({ version: '10' }).setToken(process.env.TOKEN);

		try {
    		for (const guildId of guildIds) {
        		await rest.put(
            		Routes.applicationGuildCommands(process.env.CLIENT_ID, guildId),
            		{ body: commands },
        		);
        		console.log(`✅ Registered slash commands for guild: ${guildId}`);
    		}

    		// 🚨 Clear global commands to avoid duplicates
    		await rest.put(
        		Routes.applicationCommands(process.env.CLIENT_ID),
        		{ body: [] }
    		);
    		console.log('🧹 Cleared global slash commands');
		} catch (error) {
    		console.error('❌ Error registering slash commands:', error);
		}


        // Log bot uptime every hour
        setInterval(() => {
            const uptime = process.uptime();
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            const seconds = Math.floor(uptime % 60);
            console.log(`⏱ Bot uptime: ${hours}h ${minutes}m ${seconds}s`);
        }, 3600000);

        // Activity rotation
        const activities = [
            { name: '/help for commands', type: ActivityType.Watching },
            { name: 'events in BMTG', type: ActivityType.Playing },
            { name: 'members chatting', type: ActivityType.Listening },
            { name: 'cool updates rolling out!', type: ActivityType.Watching },
            { name: 'OwO', type: ActivityType.Playing },
            { name: 'music in VC', type: ActivityType.Listening },
            { name: 'BMTG for gaws', type: ActivityType.Watching },
            { name: 'Dank Memer', type: ActivityType.Playing },
            { name: 'commands with &', type: ActivityType.Listening },
            { name: 'BMTG on Youtube', type: ActivityType.Watching },
        ];

        let index = 0;

        setInterval(() => {
            const activity = activities[index];
            client.user.setPresence({
                activities: [{ name: activity.name, type: activity.type }],
                status: process.env.ACTIVITY_STATUS || 'online',
            });
            index = (index + 1) % activities.length;
        }, 10000);

        // 🔔 Daily Reminder Task — runs at 12:30 PM IST (7:00 AM UTC)
        cron.schedule('0 30 12 * * *', () => {
            console.log('🔔 Reminder triggered!');
            
            const channel1 = client.channels.cache.get(CHANNEL_ID_1);
            if (channel1) {
                channel1.send(MESSAGE_1).catch(console.error);
            } else {
                console.log('❌ Cookie reminder channel not found.');
            }

            const channel2 = client.channels.cache.get(CHANNEL_ID_2);
            if (channel2) {
                channel2.send(MESSAGE_2).catch(console.error);
            } else {
                console.log('❌ Clover reminder channel not found.');
            }
        }, {
            timezone: 'Asia/Kolkata'
        });

        console.log('✅ Daily reminders are scheduled for cookie and clover.');
    },
};
