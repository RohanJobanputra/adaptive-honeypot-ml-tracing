This repository contains an end-to-end operational system that goes beyond traditional honeypots by actively detecting automated bots using machine learning and ethically tracing leaked decoy data.

The system is designed as a research-grade pipeline, not a demo — each module must be executed in the correct order for meaningful results.

⚠️ IMPORTANT 
This is a sequential system.
Skipping steps or changing the execution order will break the pipeline.

Prerequisites-
Ensure the following are installed before starting:
Python 3.9+
Node.js 18+
MongoDB (local or Atlas)
Git
Jupyter Notebook (optional, for retraining)

Project Structure
adaptive-honeypot-ml-tracing/
│
├── public/
│   ├── index.html              # Honeypot frontend
│   └── dashboard.html          # Visualization dashboard
│
├── server.js                   # Express server (logging + UID assignment)
├── trace.js                    # Ethical tracing module
│
├── botsimulator.py             # Automated bot traffic generator
├── humansimulatorv2.py         # Optional scripted human behavior
│
├── HoneypotMLfile.ipynb        # ML training & feature engineering
├── ml_server.py                # FastAPI ML inference server
├── bot_detection_model.joblib  # Trained ML model
├── feature_columns.joblib      # Feature schema
│
├── honeypotLogsNew.csv         # Processed interaction logs
├── models/                     # MongoDB schemas
├── routes/                     # Express routes
│
├── .env                        # GitHub token (ignored)
├── .gitignore
└── README.md

Step-by-Step Execution Guide
Follow This Order Strictly
1️⃣ Start the Honeypot Server (Logging Layer)

This server:
serves the honeypot interface
assigns unique decoy identifiers (UIDs)
logs all interactions to MongoDB + CSV

Install Node dependencies
npm install
Start the server
node server.js
✅ Expected Output
Server running on http://localhost:3000
MongoDB connected successfully

⚠️ Do NOT proceed unless this server is running

2️⃣ Generate Traffic (Human + Bot)
The system requires interaction data before ML detection or tracing can work.

2.1 Human Traffic (Manual)
Open in browser:
http://localhost:3000
Manually:
fill forms
click buttons
submit fake credentials

✅ These actions simulate legitimate human behavior.

2.2 Bot Traffic (Automated)
Run the bot simulator:
python botsimulator.py
This script:
mimics scraping / form-filling bots
sends repeated requests
causes decoy UID exposure

✅ Expected Output
Simulating bot requests...
Bot interactions logged successfully

📌 At this point:

MongoDB is populated

CSV logs are generated

3️⃣ Train or Load the ML Bot Detection Model

⚠️ Traffic must exist before this step

Option A: Use Pretrained Model (Recommended)
Already included:
bot_detection_model.joblib
feature_columns.joblib

➡️ No action needed.

Option B: Retrain the Model (Optional)
Open:
HoneypotMLfile.ipynb
Run all cells to:
extract behavioral features
train the classifier
save updated .joblib files

4️⃣ Start the ML Inference Server

This module classifies interactions as bot or human.

Install Python dependencies
pip install fastapi uvicorn pandas scikit-learn joblib
Start the ML server
uvicorn ml_server:app --reload
✅ Expected Output
Uvicorn running on http://127.0.0.1:8000

5️⃣ Bot Classification (Implicit Step)

At this stage:
logged interactions are passed to the ML model
UIDs are labeled as:
human
bot

⚠️ Do NOT run tracing unless bots are identified

6️⃣ Run the Ethical Tracing Module 

This module performs controlled post-exploitation tracing by:
selecting bot-flagged decoy UIDs
publishing decoys to monitored surfaces
observing external re-appearance
collecting verifiable leakage evidence

Prerequisite
Create .env (already git-ignored):
GITHUB_TOKEN=your_personal_access_token

Run tracing
node trace.js
