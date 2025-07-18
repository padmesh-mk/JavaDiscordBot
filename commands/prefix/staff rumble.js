module.exports = {
    name: 'bat',
    description: 'Ping for staff battles (staff battles member only)',
    async execute(message, args) {
        const allowedRoleId = '1315719570396414144'; // Replace with the actual role ID

        // Check if the user has the specific role
        if (!message.member.roles.cache.has(allowedRoleId)) {
            return message.reply('You do not have permission to use this command!');
        }

        try {
            // Delete the original command message
            await message.delete();

            // Construct the message to send
            const extraText = args.join(' ');
            const battleMessage = '<@&1313012309312012390>';

            // Send the message with any extra arguments added below the main ping
            await message.channel.send(extraText ? `${battleMessage}\n\n${extraText}` : battleMessage);
        } catch (error) {
            console.error('Error executing the bat command:', error);
            message.channel.send('There was an error trying to execute that command!');
        }
    },
};
