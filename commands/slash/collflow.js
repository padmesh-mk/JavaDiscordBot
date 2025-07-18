const { SlashCommandBuilder, MessageFlags, Collection, EmbedBuilder } = require('discord.js');

const REQUIRED_ROLE_ID = '1385315561981874287';
const flowStates = new Collection();

const flowMessages = [
    user => `wheart ${user}`,
    user => `wwater ${user}`,
    user => `wcake ${user}`,
    user => `wdish ${user}`,
    user => `wrum ${user}`,
    user => `wcupachicake ${user}`,
    user => `wcrown ${user}`,
    user => `wtaco ${user}`,
    user => `wchicken ${user}`,
    user => `wmilk ${user}`,
    user => `wmochi ${user}`,
    user => `wdonut ${user}`,
    user => `wcoffee ${user}`,
    user => `wpancakes ${user}`,
    user => `wgrizzly ${user}`,
    user => `wteddy ${user}`,
    user => `wsunflower ${user}`,
    user => `wwolf ${user}`,
    user => `wmagic ${user}`,
    user => `wpizza ${user}`,
    user => `wfrogegg ${user}`,
    user => `wpanda ${user}`,
    user => `wslime ${user}`,
    user => `wsnake ${user}`,
    user => `wlilbee ${user}`,
    user => `wmoe ${user}`,
    user => `wcompliment ${user}`,
    user => `wlarry ${user}`,
    user => `wlollipop ${user}`
];

module.exports = {
    data: new SlashCommandBuilder()
        .setName('coll')
        .setDescription('Start or end a coll flow')
        .addSubcommand(sub =>
            sub.setName('flow')
                .setDescription('Start a coll flow with a user')
                .addUserOption(opt =>
                    opt.setName('user')
                        .setDescription('User to flow with')
                        .setRequired(true)))
        .addSubcommand(sub =>
            sub.setName('flow_end')
                .setDescription('End the current flow')),

    async execute(interaction) {
        const member = interaction.member;

        if (!member.roles.cache.has(REQUIRED_ROLE_ID)) {
            return interaction.reply({
                content: 'You do not have permission to use this command.',
                flags: MessageFlags.Ephemeral
            });
        }

        const sub = interaction.options.getSubcommand();
        const guildId = interaction.guild.id;

        if (sub === 'flow') {
            const user = interaction.options.getUser('user');
            const mention = `<@${user.id}>`;

            flowStates.set(guildId, {
                targetUserId: user.id,
                step: 0,
                lastMessageId: null,
                channelId: interaction.channel.id
            });

            await interaction.reply({
                content: 'Flow started.',
                flags: MessageFlags.Ephemeral
            });

            const msg = flowMessages[0](mention);
            const sentMsg = await interaction.channel.send({
                content: msg,
                allowedMentions: { users: [] } // ping off
            });

            flowStates.get(guildId).lastMessageId = sentMsg.id;

        } else if (sub === 'flow_end') {
            if (flowStates.has(guildId)) {
                flowStates.delete(guildId);
                await interaction.reply({
                    content: 'Flow ended.',
                    flags: MessageFlags.Ephemeral
                });
            } else {
                await interaction.reply({
                    content: 'No active flow to end.',
                    flags: MessageFlags.Ephemeral
                });
            }
        }
    },

    onMessage: async (message) => {
        if (message.author.bot || !message.guild) return;

        const state = flowStates.get(message.guild.id);
        if (!state || message.author.id !== state.targetUserId) return;

        const mention = `<@${message.author.id}>`;
        const expected = flowMessages[state.step](mention);

        // Accept input that starts with the expected word (e.g. "wheart")
        if (!message.content.trim().toLowerCase().startsWith(expected.split(' ')[0])) return;

        try {
            const lastMsg = await message.channel.messages.fetch(state.lastMessageId);
            if (lastMsg) await lastMsg.delete().catch(() => {});
        } catch (err) {
            console.warn('Could not delete previous flow message:', err.message);
        }

        state.step++;

        if (state.step < flowMessages.length) {
            const nextMsg = flowMessages[state.step](mention);
            const sent = await message.channel.send({
                content: nextMsg,
                allowedMentions: { users: [] } // Ping off
            });

            state.lastMessageId = sent.id;
        } else {
            await message.channel.send({
                content: `${mention}, flow complete! 🎉`,
                allowedMentions: { users: [] }
            });
            flowStates.delete(message.guild.id);
        }
    }
};
