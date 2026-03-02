import random
import time
import uuid
from datetime import datetime, timezone
from pymongo import MongoClient

# =========================
# MongoDB Connection
# =========================
client = MongoClient("mongodb://localhost:27017/")
db = client["honeypot_logs"]
collection = db["logs"]

print("🟢 Connected to MongoDB")

# =========================
# Human-like Data Pools
# =========================
HUMAN_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) Mobile Safari"
]

REFERRERS = [
    "https://google.com",
    "https://linkedin.com",
    "https://reddit.com",
    "https://twitter.com",
    ""
]

HUMAN_INTERACTIONS = [
    "page_view",
    "scroll",
    "form_focus",
    "click_button",
    "time_on_page"
]

# =========================
# Helpers
# =========================
def fake_ip():
    return ".".join(str(random.randint(10, 240)) for _ in range(4))

def now_utc():
    return datetime.now(timezone.utc)

# =========================
# Human Session Generator
# =========================
def simulate_human_session():
    session_id = str(uuid.uuid4())
    ip = fake_ip()
    ua = random.choice(HUMAN_USER_AGENTS)
    ref = random.choice(REFERRERS)

    actions = random.randint(3, 7)

    for _ in range(actions):
        log = {
            "ip": ip,
            "userAgent": ua,
            "referrer": ref,
            "uniqueUserId": session_id,
            "interactionType": random.choice(HUMAN_INTERACTIONS),
            "details": {
                "session": session_id
            },
            "botScore": random.randint(0, 2),
            "classification": "human",
            "timestamp": now_utc()
        }

        collection.insert_one(log)
        print("👤 Human action logged")

        time.sleep(random.uniform(2, 8))  # human pacing

# =========================
# Main Loop
# =========================
if __name__ == "__main__":
    print("🚶 Starting Human Simulator v2")

    while True:
        simulate_human_session()
        time.sleep(random.uniform(5, 15))
