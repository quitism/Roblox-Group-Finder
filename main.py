import os
import sys
import threading
import random
import requests
from dhooks import Webhook

# ─── Console Title (Windows Only) ────────────────────────────────
if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("Aleks Group Finder")
    except Exception:
        pass

# ─── Configuration via ENVIRONMENT VARIABLES ────────────────────
webhook_url = os.getenv("WEBHOOK_URL")
if not webhook_url:
    print("FATAL: You must set the WEBHOOK_URL environment variable.")
    sys.exit(1)

try:
    max_threads = int(os.getenv("THREADS", "10"))
except ValueError:
    print("WARNING: THREADS must be an integer. Defaulting to 10.")
    max_threads = 10

hook = Webhook(webhook_url)

# ─── The Scanner Function ────────────────────────────────────────
def groupfinder():
    try:
        gid = random.randint(1_000_000, 1_150_000)
        page = requests.get(f"https://www.roblox.com/groups/group.aspx?gid={gid}", timeout=30)
        if 'owned' not in page.text:
            api = requests.get(f"https://groups.roblox.com/v1/groups/{gid}", timeout=30)
            if api.status_code != 429:
                data = api.json()
                if 'errors' not in data:
                    if not data.get('isLocked', True) and data.get('publicEntryAllowed') and data.get('owner') is None:
                        hook.send(f"Hit: https://www.roblox.com/groups/group.aspx?gid={gid}")
                        print(f"[+] Hit: {gid}")
                    else:
                        print(f"[-] No Entry Allowed or Locked: {gid}")
            else:
                print("[-] API Rate Limited")
        else:
            print(f"[-] Already Owned: {gid}")
    except Exception:
        pass

# ─── Launch Loop ─────────────────────────────────────────────────
print("\n🚀 Starting Aleks Group Finder with "
      f"{max_threads} threads and webhook {webhook_url}\n")

while True:
    # spawn new threads up to the limit
    if threading.active_count() - 1 < max_threads:
        threading.Thread(target=groupfinder, daemon=True).start()
    # slight pause to avoid busy-spin
    threading.Event().wait(0.1)
