const { WebhookClient } = require('discord.js');
require('dotenv').config();

const WEBHOOK_URL = process.env.LOG_WEBHOOK_URL;

let webhook;

if (WEBHOOK_URL) {
  webhook = new WebhookClient({ url: WEBHOOK_URL });
} else {
  console.warn('[logWebhook] LOG_WEBHOOK_URL not set in .env');
}

function sendLog(content) {
  if (!webhook) return;

  const chunks = content.match(/[\s\S]{1,1900}/g) || [];
  for (const chunk of chunks) {
    webhook.send({ content: chunk }).catch(console.error);
  }
}

module.exports = {
  sendLog
};
