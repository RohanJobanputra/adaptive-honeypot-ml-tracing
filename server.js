const express = require("express");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");
const axios = require("axios");

const Log = require("./models/Log");
const Trace = require("./models/trace");

const app = express();

/* ---------------- MIDDLEWARE ---------------- */
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(express.static("public"));

/* ---------------- DB ---------------- */
mongoose.connect("mongodb://127.0.0.1:27017/honeypot_logs")
  .then(() => console.log("✅ MongoDB connected"))
  .catch(err => console.error(err));

/* ---------------- UID ---------------- */
function ensureUID(req, res) {
  if (!req.cookies.uid) {
    const uid = "u_" + Math.random().toString(36).slice(2);
    res.cookie("uid", uid, { httpOnly: true });
    req.cookies.uid = uid;
  }
}

/* ---------------- CORE LOGIC ---------------- */
async function logInteraction(req, type) {

  // ✅ DECLARED ONCE — FIXES ReferenceError FOREVER
  let botScore = null;
  let classification = "unknown";

  const ua = req.headers["user-agent"] || "";
  const ip = req.socket.remoteAddress;
  const ref = req.headers.referer || "";
  const hour = new Date().getHours();

  const explicitUid =
    (req.query && req.query.uid) ||
    (req.body && (req.body.uniqueUserId || req.body.uid));

  const uid = explicitUid || req.cookies.uid || ip;

  /* ---- FREQUENCY FEATURES ---- */
  const ip_freq = Math.max(await Log.countDocuments({ ip }), 1);
  const uid_freq = Math.max(await Log.countDocuments({ uniqueUserId: uid }), 1);

  const features = {
    userAgent_len: ua.length,
    ua_bot_keyword: /bot|crawl|spider|scrapy|wget|curl|python/i.test(ua) ? 1 : 0,
    referrer_present: ref ? 1 : 0,
    night_activity: hour >= 0 && hour <= 5 ? 1 : 0,
    ip_freq,
    uid_freq
  };

  /* ---- ML SCORE ---- */
  try {
    const ml = await axios.post("http://127.0.0.1:8000/predict", features, {
      timeout: 2000
    });

    botScore = Number(ml.data.score);
    console.log("🧠 ML score:", botScore);
  } catch (err) {
    console.error("❌ ML error:", err.message);
    botScore = null;
  }

  /* ---- DECISION ENGINE ---- */
  if (botScore === null) classification = "unknown";
  else if (botScore >= 0.75) classification = "bot";
  else if (botScore >= 0.6) classification = "suspicious";
  else classification = "human";

  /* ---- HUMAN SAFETY ---- */
  if (
    classification !== "bot" &&
    features.ua_bot_keyword === 0 &&
    features.referrer_present === 1 &&
    ip_freq <= 2 &&
    uid_freq <= 2 &&
    type === "page_view"
  ) {
    classification = "human";
  }

  /* ---- HONEYPOT CONFIRMATION (SAFE) ---- */
  if (
    type !== "page_view" &&
    botScore !== null &&
    botScore >= 0.6
  ) {
    classification = "bot";
  }

  /* ---- STORE LOG ---- */
  await Log.create({
    ip,
    userAgent: ua,
    referrer: ref,
    interactionType: type,
    botScore,
    classification,
    timestamp: new Date(),
    uniqueUserId: uid
  });
}

/* ---------------- ROUTES ---------------- */

app.get("/api/pageview", async (req, res) => {
  ensureUID(req, res);
  await logInteraction(req, "page_view");
  res.send("Page viewed");
});

app.get("/api/hidden", async (req, res) => {
  ensureUID(req, res);
  await logInteraction(req, "hidden_link");
  res.sendStatus(404);
});

app.post("/api/decoy", async (req, res) => {
  ensureUID(req, res);
  await logInteraction(req, "decoy_form");
  res.redirect("/");
});

/* ---------------- DASHBOARD API ---------------- */
app.get("/api/logs", async (req, res) => {
  const logs = await Log.find()
    .sort({ timestamp: -1 })
    .limit(100)
    .lean();

  const uids = logs.map(l => l.uniqueUserId).filter(Boolean);

  const traces = await Trace.find({
    uniqueUserId: { $in: uids }
  }).lean();

  const traceMap = {};
  traces.forEach(t => {
    traceMap[t.uniqueUserId] = {
      leakUrls: t.leakUrls,
      timestamp: t.timestamp
    };
  });

  const enrichedLogs = logs.map(log => ({
    ...log,
    traceStatus: traceMap[log.uniqueUserId] ? "Traced" : "Not Traced",
    leakUrls: traceMap[log.uniqueUserId]?.leakUrls || [],
    traceTimestamp: traceMap[log.uniqueUserId]?.timestamp || null
  }));

  res.json(enrichedLogs);
});

app.get("/dashboard", (req, res) => {
  res.sendFile(__dirname + "/public/dashboard.html");
});

/* ---------------- START ---------------- */
app.listen(3000, () => {
  console.log("🚀 Server running on port 3000");
});
