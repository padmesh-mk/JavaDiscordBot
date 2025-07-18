const { Events } = require('discord.js');

module.exports = {
  name: Events.MessageCreate,
  async execute(message) {
    // Ignore messages without the trigger phrase
    if (!message.content.includes('Distorted animals are now available for')) return;

    // Regex to find time parts like 5H 45M 48S (any combination)
    const timeRegex = /(\d+)H|(\d+)M|(\d+)S/gi;

    let hours = 0, minutes = 0, seconds = 0;

    let match;
    // Run regex globally to find all parts
    while ((match = timeRegex.exec(message.content)) !== null) {
      if (match[1]) hours = parseInt(match[1]);
      if (match[2]) minutes = parseInt(match[2]);
      if (match[3]) seconds = parseInt(match[3]);
    }

    const totalSeconds = (hours * 3600) + (minutes * 60) + seconds;

    if (totalSeconds <= 0) return; // no valid time found

    const now = Math.floor(Date.now() / 1000);
    const endTimestamp = now + totalSeconds;

    // Send timestamps in chat
    message.channel.send({
      content: `<t:${endTimestamp}:R>\n<t:${endTimestamp}:T>`,
      allowedMentions: { parse: [] }
    });
  }
};
