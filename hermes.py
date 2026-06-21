from groq import Groq
from dotenv import load_dotenv
import os
import json
import schedule
import threading
import time

from skills.summarize import run as summarize_skill

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MEMORY_FILE = "memory/memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


memory = load_memory()


# =========================
# AUTONOMOUS RUN
# =========================

def auto_status():
    print("\n========================")
    print("[AUTONOMOUS RUN]")
    print("========================")

    print("What I Did:")
    print("- Stored memory successfully")

    print("\nWhat's Left:")
    print("- Connect Slack")
    print("- Connect OpenClaw")

    print("\nWhat Needs Your Call:")
    print("- Approve next development phase")

    print("\nCurrent Memory:")
    print(memory.get("fact", "Nothing stored"))

    print("========================\n")


schedule.every(1).minutes.do(auto_status)


def scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)


threading.Thread(
    target=scheduler_loop,
    daemon=True
).start()


# =========================
# MAIN LOOP
# =========================

while True:
    user = input("\nYou: ").strip()

    # Memory Save
    if user.lower().startswith("remember"):
        fact = user.replace("remember", "").strip()

        memory["fact"] = fact
        save_memory(memory)

        print("Hermes: Memory saved.")
        continue

    # Memory Recall
    if user.lower() == "recall":
        print("Hermes:", memory.get("fact", "Nothing stored"))
        continue

    # Custom Skill
    if user.lower().startswith("summarize:"):
        text = user.replace("summarize:", "").strip()

        result = summarize_skill(text)

        print("\nHermes Skill Output:")
        print(result)
        continue

    # LLM Request
    prompt = f"""
You are Hermes Agent.

Before answering:
1. Create a PLAN.
2. Then provide EXECUTION.

User Request:
{user}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        print("\nHermes:")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"\nError: {e}")