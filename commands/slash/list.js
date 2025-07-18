const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('list')
    .setDescription("Manage your personal list")
    .addSubcommand(sub => 
      sub.setName('show')
         .setDescription('Show your to-buy list')
    )
    .addSubcommand(sub =>
      sub.setName('add')
         .setDescription('Add an item to the list')
         .addStringOption(opt =>
           opt.setName('item')
              .setDescription('Item to add')
              .setRequired(true)
         )
    )
    .addSubcommand(sub =>
      sub.setName('remove')
         .setDescription('Remove an item from the list')
         .addStringOption(opt =>
           opt.setName('item')
              .setDescription('Item to remove')
              .setRequired(true)
         )
    ),
  async execute(interaction) {
    const allowedUserId = '941902212303556618'; // 👈 Replace with your actual user ID

    if (interaction.user.id !== allowedUserId) {
      return await interaction.reply({ content: "❌ You can't use this command.", ephemeral: true });
    }

    const sub = interaction.options.getSubcommand();
    const fs = require('fs');
    const filePath = './list.json';

    // Load or initialize list
    let listData = [];
    if (fs.existsSync(filePath)) {
      listData = JSON.parse(fs.readFileSync(filePath));
    }

    if (sub === 'show') {
      const embed = {
        title: "Padmesh's To-Buy List!!",
        color: 0x800080,
        description: listData.map((item, i) => `⇀ ${item}`).join("\n") || "No items in the list.",
        footer: {
          text: `Total Items: ${listData.length} | Collector – Items: 94%`
        }
      };

      await interaction.reply({ embeds: [embed] });
    }

    if (sub === 'add') {
      const item = interaction.options.getString('item');
      if (listData.includes(item)) {
        return await interaction.reply({ content: `⚠️ \`${item}\` is already in the list.`, ephemeral: true });
      }
      listData.push(item);
      fs.writeFileSync(filePath, JSON.stringify(listData, null, 2));
      await interaction.reply({ content: `✅ Added \`${item}\` to your list.` });
    }

    if (sub === 'remove') {
      const item = interaction.options.getString('item');
      if (!listData.includes(item)) {
        return await interaction.reply({ content: `❌ \`${item}\` not found in the list.`, ephemeral: true });
      }
      listData = listData.filter(i => i !== item);
      fs.writeFileSync(filePath, JSON.stringify(listData, null, 2));
      await interaction.reply({ content: `🗑️ Removed \`${item}\` from your list.` });
    }
  }
};
