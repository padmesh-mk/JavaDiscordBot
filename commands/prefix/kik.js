module.exports = {
    name: 'kik',
    description: 'Kick a user with a default reason.',
    async execute(message, args) {
        // Define the allowed roles by their IDs or names
        const allowedRoles = ['1335128922446237696', '1313556608474812527', '1313596462621265932', '1206626888811020368', '1214099642908934155']; // Replace with actual role names or IDs

        // Check if the member has one of the allowed roles
        const hasPermission = message.member.roles.cache.some(
            (role) => allowedRoles.includes(role.name) || allowedRoles.includes(role.id)
        );

        if (!hasPermission) {
            return message.reply('You do not have permission to use this command.');
        }

        // Check if a user was mentioned
        const member = message.mentions.members.first() || message.member;
        const reason = args.slice(1).join(' ') || 'no reason';

        // Delete the original command message
        await message.delete();

        // Send the ban message
        message.channel.send(`Kicked **${member.user.tag}** Reason: ${reason}`);
    },
};
