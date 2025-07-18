const { Client, Collection, GatewayIntentBits } = require('discord.js');
const fs = require('fs');
const path = require('path');
require('dotenv').config();
const { sendLog } = require('./logWebhook'); // Webhook logger

const { TOKEN, PREFIX, GUILD_ID } = process.env;

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.DirectMessages,
        GatewayIntentBits.GuildMembers
    ]
});

client.commands = new Collection();
client.prefixCommands = new Collection();
client.cooldowns = new Collection();

// Load commands
const loadCommands = () => {
    const commandFolders = fs.readdirSync('./commands');
    for (const folder of commandFolders) {
        const commandFiles = fs.readdirSync(`./commands/${folder}`).filter(file => file.endsWith('.js'));

        for (const file of commandFiles) {
            const commandPath = `./commands/${folder}/${file}`;
            const command = require(commandPath);

            try {
                if (folder === 'slash') {
                    if (command?.data?.name) {
                        client.commands.set(command.data.name, command);
                        console.log(`✅ Slash command loaded: ${command.data.name}`);
                    } else {
                        console.warn(`⚠️ Skipped invalid slash command: ${file}`);
                    }
                } else if (folder === 'prefix') {
                    if (command?.name && typeof command.execute === 'function') {
                        client.prefixCommands.set(command.name, command);
                        console.log(`✅ Prefix command loaded: ${command.name}`);
                    } else {
                        console.warn(`⚠️ Skipped invalid prefix command: ${file}`);
                    }
                } else {
                    if (command?.name && typeof command.execute === 'function') {
                        client.commands.set(command.name, command);
                        console.log(`✅ Generic command loaded: ${command.name}`);
                    } else {
                        console.warn(`⚠️ Skipped invalid command in ${folder}: ${file}`);
                    }
                }
            } catch (err) {
                console.error(`❌ Error loading command ${file}:`, err.message);
            }
        }
    }

    console.log(`📦 Loaded ${client.commands.size} slash commands`);
    console.log(`📦 Loaded ${client.prefixCommands.size} prefix commands`);
};

// Register slash commands per guild
const registerSlashCommands = async () => {
    const commands = client.commands.map(command => command.data.toJSON());
    try {
        const guild = await client.guilds.fetch(GUILD_ID);
        if (!guild) {
            return console.error('❌ Guild not found. Check your GUILD_ID in .env');
        }

        await guild.commands.set(commands); // Per-guild registration
        console.log(`✅ Slash commands registered to guild: ${guild.name}`);
    } catch (error) {
        console.error('❌ Error registering slash commands:', error);
    }
};

// Optional: Clear global slash commands once (if needed)
/*
const clearGlobalCommands = async () => {
    try {
        await client.application.commands.set([]);
        console.log('🧹 Cleared global slash commands');
    } catch (err) {
        console.error('❌ Failed to clear global commands:', err.message);
    }
};
*/

// Load events
const loadEvents = () => {
    const eventFiles = fs.readdirSync('./events').filter(file => file.endsWith('.js'));
    for (const file of eventFiles) {
        const event = require(`./events/${file}`);
        if (event.once) {
            client.once(event.name, (...args) => event.execute(...args, client));
        } else {
            client.on(event.name, (...args) => event.execute(...args, client));
        }
    }
};

// Handle message triggers
const loadTriggers = () => {
    client.on('messageCreate', async (message) => {
        if (message.author.bot || !message.guild) return;

        const triggerFiles = fs.readdirSync('./commands/triggers').filter(file => file.endsWith('.js'));

        for (const file of triggerFiles) {
            const trigger = require(`../commands/triggers/${file}`);
            if (trigger && typeof trigger.execute === 'function') {
                try {
                    await trigger.execute(message);
                } catch (err) {
                    console.error(`❌ Error in trigger ${file}:`, err.message);
                }
            }
        }
    });
};

// On bot ready
client.once('ready', async () => {
    console.log(`🤖 Logged in as ${client.user.tag}`);
    await registerSlashCommands();
    // await clearGlobalCommands(); // Optional
});

// Start bot
const startBot = () => {
    loadCommands();
    loadEvents();
    loadTriggers();

    client.login(TOKEN).catch(err => console.error(`❌ Error logging in: ${err.message}`));

    // Override logging with webhook
    const originalLog = console.log;
    console.log = (...args) => {
        const message = args.join(' ');
        originalLog(...args);
        sendLog(message);
    };

    const originalError = console.error;
    console.error = (...args) => {
        const message = args.join(' ');
        originalError(...args);
        sendLog(`❌ ERROR: ${message}`);
    };
};

startBot();
