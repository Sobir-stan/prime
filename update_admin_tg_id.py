#!/usr/bin/env python
"""Update admin user with telegram_id."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.db"

if not DB_PATH.exists():
    print(f"Database not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# The user's telegram ID from earlier conversation
ADMIN_TG_ID = 7374825920

print("\n" + "="*80)
print("UPDATE ADMIN WITH TELEGRAM ID")
print("="*80)

# Check current state
print("\nBEFORE:")
print("-" * 80)
cur.execute("SELECT id, username, telegram_id FROM users WHERE username = 'admin'")
row = cur.fetchone()
if row:
    print(f"  ID: {row[0]}")
    print(f"  Username: {row[1]}")
    print(f"  Telegram ID: {row[2] if row[2] else '(None)'}")

# Update admin with telegram_id
print("\nUPDATING...")
print("-" * 80)
cur.execute("UPDATE users SET telegram_id = ? WHERE username = 'admin'", (ADMIN_TG_ID,))
conn.commit()
print(f"  Updated admin user with telegram_id = {ADMIN_TG_ID}")

# Verify
print("\nAFTER:")
print("-" * 80)
cur.execute("SELECT id, username, telegram_id FROM users WHERE username = 'admin'")
row = cur.fetchone()
if row:
    print(f"  ID: {row[0]}")
    print(f"  Username: {row[1]}")
    print(f"  Telegram ID: {row[2]}")

# Show all users
print("\nALL USERS:")
print("-" * 80)
cur.execute("SELECT id, username, telegram_id FROM users ORDER BY id")
rows = cur.fetchall()
for row in rows:
    tg_id = row[2] if row[2] else "(None)"
    print(f"  {row[0]}. {row[1]:<15} - telegram_id = {tg_id}")

conn.close()

print("\n" + "="*80)
print("DONE! Admin account now has telegram_id stored.")
print("="*80 + "\n")

