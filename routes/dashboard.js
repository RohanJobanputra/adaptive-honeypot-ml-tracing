const express = require('express');
const router = express.Router();
const Log = require('../models/Log');

/* Serve dashboard page */
router.get('/dashboard', (req, res) => {
  res.sendFile('dashboard.html', { root: 'public' });
});

/* API to fetch logs */
router.get('/api/logs', async (req, res) => {
  try {
    const logs = await Log.find().sort({ timestamp: -1 }).limit(200);
    res.json(logs);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch logs' });
  }
});

module.exports = router;
