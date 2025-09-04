const { Events } = require("discord.js");

module.exports = {
  name: Events.MessageCreate,
  async execute(message) {
    // Skip bot messages
    if (message.author.bot) return;

    // Combine message content and embed text
    let text = message.content;
    if (message.embeds.length > 0) {
      for (const embed of message.embeds) {
        if (embed.title) text += " " + embed.title;
        if (embed.description) text += " " + embed.description;
        if (embed.fields) {
          for (const field of embed.fields) {
            text += " " + field.name + " " + field.value;
          }
        }
        if (embed.footer?.text) text += " " + embed.footer.text;
      }
    }

    // Regex for days, hours, minutes, seconds (order doesn’t matter)
    const timeRegex = /(\d+)\s*d|(\d+)\s*h|(\d+)\s*m|(\d+)\s*s/gi;

    let days = 0,
      hours = 0,
      minutes = 0,
      seconds = 0;

    let match;
    while ((match = timeRegex.exec(text)) !== null) {
      if (match[1]) days = parseInt(match[1]);
      if (match[2]) hours = parseInt(match[2]);
      if (match[3]) minutes = parseInt(match[3]);
      if (match[4]) seconds = parseInt(match[4]);
    }

    const totalSeconds =
      days * 86400 + hours * 3600 + minutes * 60 + seconds;

    if (totalSeconds <= 0) return; // no valid time found

    const now = Math.floor(Date.now() / 1000);
    const endTimestamp = now + totalSeconds;

    // Reply with timestamp
    message.channel.send({
      content: `<t:${endTimestamp}:R>\n<t:${endTimestamp}:T>`,
      allowedMentions: { parse: [] },
    });
  },
};
