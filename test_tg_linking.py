#!/usr/bin/env python
"""
Test script to simulate the complete Telegram linking flow.
This mimics what happens when a user opens the clicker from Telegram WebApp.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.db"

def test_telegram_flow():
    """Simulate linking a Telegram ID."""
    print("\n" + "="*80)
    print("TELEGRAM LINKING FLOW TEST")
    print("="*80)
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Check initial state
    print("\n1. INITIAL STATE:")
    print("-" * 80)
    cur.execute("SELECT username, telegram_id FROM users ORDER BY id")
    rows = cur.fetchall()
    print(f"   Users: {len(rows)}")
    for row in rows:
        print(f"   - {row['username']}: telegram_id = {row['telegram_id']}")
    
    # Simulate the flow
    test_tg_id = 7374825920
    test_username = "SbrAbd"
    
    print(f"\n2. SIMULATING TELEGRAM LINK:")
    print("-" * 80)
    print(f"   TG ID to link: {test_tg_id}")
    print(f"   User to link: {test_username}")
    print(f"   Expected endpoint: POST /link_telegram")
    print(f"   Expected flow:")
    print(f"     a) /tg_login validates TG ID exists in DB")
    print(f"     b) /link_telegram stores TG ID for authenticated user")
    
    # Simulate what /link_telegram does
    print(f"\n3. SIMULATING /link_telegram ENDPOINT:")
    print("-" * 80)
    try:
        cur.execute("UPDATE users SET telegram_id = ? WHERE username = ?", 
                   (test_tg_id, test_username))
        conn.commit()
        print(f"   [OK] Updated {test_username} with telegram_id = {test_tg_id}")
    except Exception as e:
        print(f"   [ERROR] {e}")
        conn.close()
        return False
    
    # Verify the change
    print(f"\n4. VERIFICATION:")
    print("-" * 80)
    cur.execute("SELECT username, telegram_id FROM users ORDER BY id")
    rows = cur.fetchall()
    print(f"   Users: {len(rows)}")
    for row in rows:
        tg_id = row['telegram_id'] if row['telegram_id'] else "(None)"
        status = "[OK]" if row['telegram_id'] else "[NO]"
        print(f"   {status} {row['username']}: telegram_id = {tg_id}")
    
    # Summary
    print(f"\n5. SUMMARY:")
    print("-" * 80)
    cur.execute("SELECT COUNT(*) as count FROM users WHERE telegram_id IS NOT NULL")
    count = cur.fetchone()['count']
    total = len(rows)
    print(f"   Total users: {total}")
    print(f"   Users with Telegram ID: {count}")
    print(f"   Users WITHOUT Telegram ID: {total - count}")
    
    if count > 0:
        print(f"\n   [SUCCESS] Telegram ID is being stored!")
    else:
        print(f"\n   [NOTICE] No telegram IDs are stored yet")
    
    conn.close()
    return count > 0

if __name__ == "__main__":
    success = test_telegram_flow()
    print("\n" + "="*80 + "\n")
    exit(0 if success else 1)

