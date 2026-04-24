#!/usr/bin/env python
"""Remove telegram_id from SbrAbd account, keep only admin."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.db"

if not DB_PATH.exists():
    print(f"Database not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("\n" + "="*80)
print("CLEAN UP: REMOVE TG ID FROM SBRABD")
print("="*80)

# Check current state
print("\nBEFORE:")
print("-" * 80)
cur.execute("SELECT id, username, telegram_id FROM users ORDER BY id")
rows = cur.fetchall()
for row in rows:
    tg_id = row[2] if row[2] else "(None)"
    print(f"  {row[0]}. {row[1]:<15} - telegram_id = {tg_id}")

# Remove telegram_id from SbrAbd
print("\nREMOVING...")
print("-" * 80)
cur.execute("UPDATE users SET telegram_id = NULL WHERE username = 'SbrAbd'")
conn.commit()
print(f"  Cleared telegram_id from SbrAbd account")

# Verify
print("\nAFTER:")
print("-" * 80)
cur.execute("SELECT id, username, telegram_id FROM users ORDER BY id")
rows = cur.fetchall()
for row in rows:
    tg_id = row[2] if row[2] else "(None)"
    marker = "[YOUR ACCOUNT]" if row[1] == "admin" else "[OTHER]"
    print(f"  {row[0]}. {row[1]:<15} - telegram_id = {tg_id:<15} {marker}")

conn.close()

print("\n" + "="*80)
print("DONE! Telegram ID only stored for admin account now.")
print("="*80 + "\n")

