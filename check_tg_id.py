#!/usr/bin/env python
"""Quick script to check the users table and see if telegram_id is stored."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.db"

if not DB_PATH.exists():
    print(f"Database not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=" * 80)
print("USERS TABLE CONTENTS:")
print("=" * 80)

cur.execute("SELECT id, username, email, telegram_id FROM users")
rows = cur.fetchall()

if not rows:
    print("No users found in database.")
else:
    print(f"{'ID':<5} {'Username':<15} {'Email':<30} {'Telegram ID':<15}")
    print("-" * 80)
    for row in rows:
        tg_id = row['telegram_id'] if row['telegram_id'] else "(None)"
        print(f"{row['id']:<5} {row['username']:<15} {row['email']:<30} {tg_id:<15}")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
users_with_tg = sum(1 for row in rows if row['telegram_id'])
print(f"Total users: {len(rows)}")
print(f"Users with Telegram ID: {users_with_tg}")
print(f"Users WITHOUT Telegram ID: {len(rows) - users_with_tg}")

conn.close()

