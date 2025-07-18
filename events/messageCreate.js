const collFlowCommand = require('../commands/slash/collflow'); // Correct path

module.exports = {
    name: 'messageCreate',
    async execute(message, client) {
        // ✅ Handle coll flow logic
        if (typeof collFlowCommand.onMessage === 'function') {
            try {
                await collFlowCommand.onMessage(message);
            } catch (err) {
                console.error('Error in collFlowCommand.onMessage:', err);
            }
        }

        // Retrieve the command prefix
        const prefix = process.env.PREFIX;
        if (!message.content.startsWith(prefix) || message.author.bot) return;

        // Split the message content into arguments
        const args = message.content.slice(prefix.length).trim().split(/ +/);
        const commandName = args.shift().toLowerCase();

        // Look up the command by name or alias
        const command =
            client.prefixCommands.get(commandName) ||
            [...client.prefixCommands.values()].find(cmd => cmd.aliases?.includes(commandName));
        if (!command) return;

        // Handle cooldowns for commands
        const { cooldowns } = client;
        if (!cooldowns.has(command.name)) {
            cooldowns.set(command.name, new Map());
        }

        const now = Date.now();
        const timestamps = cooldowns.get(command.name);
        const cooldownAmount = (command.cooldown || 3) * 1000;

        if (timestamps.has(message.author.id)) {
            const expirationTime = timestamps.get(message.author.id) + cooldownAmount;
            if (now < expirationTime) {
                const timeLeft = Math.ceil((expirationTime - now) / 1000);

                if (message.cooldownMessage) {
                    try {
                        await message.cooldownMessage.edit(`Please wait **${timeLeft}** more second(s) before reusing the **${prefix}${command.name}** command.`);
                    } catch (error) {
                        return;
                    }
                } else {
                    try {
                        const cooldownMessage = await message.reply(`Please wait **${timeLeft}** more second(s) before reusing the **${prefix}${command.name}** command.`);
                        message.cooldownMessage = cooldownMessage;
                    } catch (error) {
                        return;
                    }
                }

                setTimeout(async () => {
                    if (message.cooldownMessage) {
                        try {
                            await message.cooldownMessage.delete();
                        } catch (error) {
                            return;
                        }
                    }
                }, cooldownAmount - (now - timestamps.get(message.author.id)));

                return;
            }
        }

        timestamps.set(message.author.id, now);
        setTimeout(() => timestamps.delete(message.author.id), cooldownAmount);

        try {
            await command.execute(message, args);
        } catch (error) {
            console.error(error);
            message.reply('Uh oh, an error occurred while executing this command. Please try again later.');
        }
    },
};
