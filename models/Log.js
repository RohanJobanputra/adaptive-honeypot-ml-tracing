const mongoose = require('mongoose');

const logSchema = new mongoose.Schema({
  timestamp: { type: Date, default: Date.now },
  ip: String,
  userAgent: String,
  referrer: String,
  uniqueUserId: String,
  interactionType: String,
  details: mongoose.Schema.Types.Mixed,
  botScore: Number,
  classification: String
});

module.exports = mongoose.model('Log', logSchema);
