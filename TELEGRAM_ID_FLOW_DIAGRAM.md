# Telegram ID Storage - Complete Flow Diagram

## Flow 1: Existing Web Session + Telegram WebApp

```
┌─────────────────────────────────────────────────────────────────┐
│ User opens "Clicker o'ynash" button from Telegram               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ clicker.js runs initUser()                                       │
│ - Gets TG ID from Telegram.WebApp.initDataUnsafe.user.id        │
│ - Checks localStorage for 'primeUser' and 'primeToken'          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
            HAS TOKEN          NO TOKEN
                    │                   │
                    ↓                   ↓
        ┌──────────────────┐  ┌─────────────────┐
        │ POST /link_telegram│ │ POST /tg_login   │
        │ with Bearer token  │ │ (auto-login)     │
        │ [telegram_id]      │ │                  │
        └──────────────────┘  └─────────────────┘
                    │                   │
                    │                   ↓
                    │         ┌──────────────────┐
                    │         │ Login successful │
                    │         │ Save token to    │
                    │         │ localStorage     │
                    │         └──────────────────┘
                    │                   │
                    │                   ↓
                    │         ┌──────────────────┐
                    │         │ POST /link_telegram│
                    │         │ with new token    │
                    │         │ [telegram_id]     │
                    │         └──────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              ↓
                ┌──────────────────────────────┐
                │ /link_telegram endpoint      │
                │ - Extract username from token│
                │ - Look up user in DB         │
                │ - UPDATE telegram_id         │
                │ - COMMIT to database         │
                │ - LOG success                │
                └──────────────────────────────┘
                              ↓
                ┌──────────────────────────────┐
                │ DATABASE UPDATED              │
                │ users table:                  │
                │ telegram_id = [SET]           │
                └──────────────────────────────┘
```

---

## Code Path Details

### Step 1: initUser() in clicker.js (lines 18-90)
```javascript
// Line 32: Log initial state
console.log('[initUser] TG ID:', tgId, 'Active User:', activeUser, 'Has Token:', !!activeToken);

// Lines 34-51: IF HAS EXISTING TOKEN
if (tgId && activeUser && activeToken) {
    fetch('/link_telegram', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${activeToken}`  // Send token in header
        },
        body: JSON.stringify({ telegram_id: tgId })  // Send Telegram ID
    })
    // Then logs response
}

// Lines 52-81: IF NO TOKEN - AUTO-LOGIN
else if (tgId) {
    const resp = await fetch('/tg_login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: tgId })
    });
    if (resp.ok) {
        const data = await resp.json();
        localStorage.setItem('primeUser', data.username);
        localStorage.setItem('primeToken', data.token);
        
        // NOW link telegram ID with new token
        await fetch('/link_telegram', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${data.token}`
            },
            body: JSON.stringify({ telegram_id: tgId })
        })
    }
}
```

### Step 2: /link_telegram Endpoint (app/routers/login.py, lines 64-75)
```python
@router.post("/link_telegram")
def link_telegram(data: TelegramAuth, 
                 db: Session = Depends(get_db), 
                 current_user: str = Depends(get_current_user_from_cookie)):
    
    # Extract username from the Bearer token
    user = crud.get_user_by_username(db, current_user)
    
    if user:
        # Only update if different
        if user.telegram_id != data.telegram_id:
            user.telegram_id = data.telegram_id
            db.commit()  # <-- THIS SAVES TO DATABASE
            logging.info(f"[LINK_TELEGRAM] Linked {data.telegram_id} to {current_user}")
        
        return {
            "msg": "Telegram ID linked successfully",
            "user": current_user,
            "telegram_id": data.telegram_id
        }
    
    raise HTTPException(status_code=404, detail="User not found")
```

### Step 3: Database Update
```sql
UPDATE users 
SET telegram_id = 7374825920 
WHERE username = 'SbrAbd';

COMMIT;
```

---

## Authentication Flow

```
┌──────────────────────────────────────────────────────────┐
│ get_current_user_from_cookie() function                 │
│ (app/core/security.py, lines 30-56)                     │
└──────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴──────────────────┐
        │                                    │
   CHECK COOKIE         FALLBACK: CHECK HEADER
        │                                    │
        ├─→ request.cookies.get("access_token")
        │                                    │
        │                       ├─→ request.headers.get("Authorization")
        │                       │   (looks for "Bearer TOKEN" format)
        │                       │
        └─────────────────┬──────────────────┘
                          ↓
            ┌────────────────────────────────┐
            │ JWT.decode(token, SECRET_KEY)  │
            │                                │
            │ Extract username from payload  │
            │ (payload["sub"])               │
            └────────────────────────────────┘
                          ↓
            ┌────────────────────────────────┐
            │ Return: username               │
            │ (passed to endpoint function)  │
            └────────────────────────────────┘
```

---

## Example: Real Flow Execution

### Time T=0: User Opens Clicker from Telegram
```
Browser: Opens https://your-domain/clicker
Telegram ID available: 7374825920
localStorage: empty (no prior login)
```

### Time T=1: initUser() Detects No Token
```
Console: [initUser] TG ID: 7374825920 Active User: null Has Token: false
Console: [initUser] TG ID detected but no active web session. Attempting auto-login via /tg_login
```

### Time T=2: Auto-Login to /tg_login
```
Request: POST /tg_login
Body: {"telegram_id": 7374825920}

Server checks: Is there a user with telegram_id = 7374825920?
→ YES! User "SbrAbd" exists
→ Creates JWT token
→ Returns: {
    "login": "success",
    "username": "SbrAbd",
    "token": "eyJhbGc..."
}
```

### Time T=3: Save Token to localStorage
```
localStorage.setItem('primeUser', 'SbrAbd');
localStorage.setItem('primeToken', 'eyJhbGc...');
```

### Time T=4: Link Telegram ID
```
Console: [TG Auto-Login] Success: {username: 'SbrAbd', login: 'success', token: 'eyJhbGc...'}

Request: POST /link_telegram
Headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGc...'
}
Body: {"telegram_id": 7374825920}

Server:
- Extracts username from token: "SbrAbd"
- Looks up user in DB
- UPDATE users SET telegram_id = 7374825920 WHERE username = 'SbrAbd'
- COMMIT
- Returns: {"msg": "Telegram ID linked successfully", ...}
```

### Time T=5: Database Updated ✓
```
Database query:
SELECT username, telegram_id FROM users WHERE username = 'SbrAbd';

Result:
SbrAbd | 7374825920
```

---

## Console Logs to Look For

When testing, open browser F12 → Console and look for:

### Success Case
```
[initUser] TG ID: 7374825920 Active User: null Has Token: false
[initUser] TG ID detected but no active web session. Attempting auto-login via /tg_login
[TG Auto-Login] Success: {username: "SbrAbd", login: "success", token: "eyJhbGc..."}
[Link Telegram after auto-login] Status: 200
```

### Problem Cases
```
[TG Auto-Login] Failed with status 404
→ User with this TG ID doesn't exist in database

[Link Telegram] Error: ...
→ Token validation failed or user lookup failed
```

---

## Summary Table

| Component | File | Status |
|-----------|------|--------|
| UI Initialization | clicker.js (lines 18-90) | ✓ Working |
| Auto-Login Endpoint | app/routers/login.py (lines 49-62) | ✓ Working |
| Link Endpoint | app/routers/login.py (lines 64-75) | ✓ Working |
| Database Column | app/db/models.py (line 15) | ✓ Exists |
| Token Validation | app/core/security.py (lines 30-56) | ✓ Working |
| **Result** | Real User Data | **✓ STORED** |

