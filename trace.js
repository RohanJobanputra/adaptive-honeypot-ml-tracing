require('dotenv').config();
console.log("GitHub token loaded:", !!process.env.GITHUB_TOKEN);

const mongoose = require('mongoose');
const axios = require('axios');

// --- Config ---
const BOT_SCORE_THRESHOLD = 0.75; // Only trace bots with score >= 0.75
const GITHUB_API_URL = 'https://api.github.com/gists';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

// --- MongoDB Setup ---
mongoose.connect('mongodb://localhost:27017/honeypot_logs')
  .then(() => console.log("✅ Connected to MongoDB"))
  .catch(err => console.error("❌ MongoDB connection error:", err));

// --- Schemas ---
const logSchema = new mongoose.Schema({
  timestamp: { type: Date, default: Date.now },
  ip: String,
  userAgent: String,
  referrer: String,
  uniqueUserId: String,
  interactionType: String,
  details: Object,
  botScore: Number,
  classification: String
});

const traceSchema = new mongoose.Schema({
  timestamp: { type: Date, default: Date.now },
  uniqueUserId: String,
  leakUrls: [String]
});

const Log = mongoose.model('Log', logSchema);
const Trace = mongoose.model('Trace', traceSchema);

// --- Step 1: Get recent high-confidence bot UIDs ---
async function getRecentBotUids() {
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
  const uids = await Log.find({
    classification: 'bot',
    botScore: { $gte: BOT_SCORE_THRESHOLD },
    uniqueUserId: { $ne: '' },
    timestamp: { $gte: oneHourAgo },
  }).distinct('uniqueUserId');

  console.log(`Found ${uids.length} high-confidence bots in last hour.`);
  return uids;
}

// --- Step 2: Post UID to GitHub Gist ---
async function postLeakToGist(uid) {
  const timestamp = new Date().toISOString();
  const content = `UID: ${uid}\nTimestamp: ${timestamp}`;

  console.log(`📡 Leaking UID: ${uid}`);
  console.log(`→ Posting content: "${content}"`);

  try {
    const response = await axios.post(GITHUB_API_URL, {
      description: `UID Leak: ${uid}`,
      public: true,
      files: {
        [`uid-leak-${uid}.txt`]: { content }
      }
    }, {
      headers: {
        Authorization: `token ${GITHUB_TOKEN}`,
        'User-Agent': 'honeypot-tracer'
      }
    });

    const url = response.data.html_url;
    return url;
  } catch (err) {
    console.error("❌ Gist creation error:", err.response?.data || err.message);
    return null;
  }
}

// --- Step 3: Verify UID in Gist ---
async function scanGist(url, uid) {
  try {
    const { data } = await axios.get(url);
    return data.includes(uid);
  } catch (err) {
    console.error("❌ Error fetching Gist:", err.message);
    return false;
  }
}

// --- Step 4: Main Tracer ---
async function runTracer() {
  const uids = await getRecentBotUids();

  if (uids.length === 0) {
    console.log("⚠️ No high-confidence bot UIDs found.");
    mongoose.disconnect();
    return;
  }

  for (const uid of uids) {
    const leakUrl = await postLeakToGist(uid);
    if (!leakUrl) {
      console.log("❌ Leak post failed. Skipping...");
      continue;
    }

    const found = await scanGist(leakUrl, uid);
    if (found) {
      console.log(`✅ Leak confirmed at ${leakUrl}`);
      await Trace.create({ uniqueUserId: uid, leakUrls: [leakUrl] });
    } else {
      console.log("❌ UID not found in Gist content.");
    }
  }

  mongoose.disconnect();
  console.log("✅ Tracing finished.");
}

// Run
runTracer().catch(err => {
  console.error("❌ Unhandled error:", err);
  mongoose.disconnect();
});
