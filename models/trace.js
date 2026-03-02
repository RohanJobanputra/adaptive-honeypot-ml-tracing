const mongoose = require("mongoose");

const TraceSchema = new mongoose.Schema({
  uniqueUserId: { type: String, required: true },
  leakUrls: { type: [String], default: [] },
  timestamp: { type: Date, default: Date.now }
});

module.exports = mongoose.model("Trace", TraceSchema);
