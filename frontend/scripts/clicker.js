let cookies = 0;
let totalCookies = 0;
let cps = 0;

const upgrades = {
    cursor: { baseCost: 15, cost: 15, count: 0, cpsAdd: 0.1 },
    grandma: { baseCost: 100, cost: 100, count: 0, cpsAdd: 1 },
    factory: { baseCost: 1000, cost: 1000, count: 0, cpsAdd: 8 }
};

const cookiesEl = document.getElementById('cookies');
const cpsEl = document.getElementById('cps');
const bigCookie = document.getElementById('bigCookie');
const usernameDisplay = document.getElementById('usernameDisplay');
const avatarInitial = document.getElementById('avatarInitial');

async function initUser() {
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
        const tgUser = window.Telegram.WebApp.initDataUnsafe.user;
        const tgId = tgUser.id;
        const tgUsername = tgUser.username || `user_${tgId}`;

        try {
            window.Telegram.WebApp.expand();
            const resp = await fetch('/tg_login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ telegram_id: tgId, username: tgUsername })
            });
            if (resp.ok) {
                const data = await resp.json();
                localStorage.setItem('primeUser', data.username);
                if (data.token) localStorage.setItem('primeToken', data.token);
            }
        } catch (e) {
            console.error("TG Auth error", e);
        }
    }

    const user = localStorage.getItem('primeUser');
    if (!user) {
        window.location.href = '/';
        return;
    }

    usernameDisplay.textContent = user;
    avatarInitial.textContent = user.charAt(0).toUpperCase();

    await loadProgress(user);
    // If localStorage has an equipped skin (recently purchased), apply it immediately for instant feedback
    try {
        const raw = localStorage.getItem('primeEquippedSkin');
        if (raw) {
            try {
                const equipped = JSON.parse(raw);
                if (equipped) {
                    // prefer explicit type if provided
                    if (equipped.type) applySkinVisualByType(equipped.type);
                    else if (equipped.name) applySkinVisualByName(equipped.name);
                }
            } catch (_) {
                // ignore parse error
            }
        }
    } catch (e) { console.warn('no local equipped skin', e); }
    // after local attempt, ensure server state is applied
    try { await loadAndApplyUserSkin(user); } catch (e) { console.warn('Failed to load user skin', e); }
}

// New: fetch skin summary and apply equipped skin to the cookie-wrapper
async function fetchSkinSummaryForUser(username) {
    if (!username) return null;
    try {
        const resp = await fetch(`/api/skins/summary?user_id=${encodeURIComponent(username)}`);
        if (!resp.ok) return null;
        return await resp.json();
    } catch (e) {
        console.error('fetchSkinSummaryForUser error', e);
        return null;
    }
}

function hideAllSkins() {
    const ids = ['bigCookie', 'bigEgg', 'bigOrenge', 'bigCoin'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
    });
}

function showDefaultCookie() {
    hideAllSkins();
    const c = document.getElementById('bigCookie');
    if (c) c.classList.add('active');
}

function applySkinVisualByName(name) {
    // fallback to type-based mapping if name heuristics fail
    if (!name) { showDefaultCookie(); return; }
    applySkinVisualByType(name.toLowerCase());
}

function applySkinVisualByType(type) {
    hideAllSkins();
    if (!type) { showDefaultCookie(); return; }
    const t = type.toLowerCase();
    // support both explicit type values ('egg','orange','coin','cookie') and fallback names
    if (t === 'egg' || t.includes('egg')) {
        const e = document.getElementById('bigEgg'); if (e) { e.classList.add('active'); return; }
    }
    if (t === 'orange' || t.includes('orange') || t.includes('apels')) {
        const o = document.getElementById('bigOrenge'); if (o) { o.classList.add('active'); return; }
    }
    if (t === 'coin' || t.includes('coin') || t.includes('tanga')) {
        const co = document.getElementById('bigCoin'); if (co) { co.classList.add('active'); return; }
    }
    // cookie or default
    const c = document.getElementById('bigCookie'); if (c) { c.classList.add('active'); return; }
    showDefaultCookie();
}

async function loadAndApplyUserSkin(username) {
    const summary = await fetchSkinSummaryForUser(username);
    if (!summary) return;
    // summary.owned contains objects with equipped flag
    if (Array.isArray(summary.owned)) {
        const equipped = summary.owned.find(s => s.equipped === true);
        if (equipped) {
            // apply visual by name
            applySkinVisualByName(equipped.name);
            // clear localStorage marker since server state is authoritative now
            try { localStorage.removeItem('primeEquippedSkin'); } catch (_) {}
            return;
        }
    }
    // if nothing equipped, show default
    showDefaultCookie();
}

// Expose helper to clear local primeEquippedSkin (for tests / manual reset)
if (typeof window !== 'undefined') window.clearLocalEquippedSkin = function() { try { localStorage.removeItem('primeEquippedSkin'); } catch(_){} };

async function loadProgress(username) {
    try {
        const token = localStorage.getItem('primeToken') || '';
        const response = await fetch(`/load_progress/${username}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const data = await response.json();

            cookies = data.cookies;
            totalCookies = data.totalCookies;

            upgrades.cursor.count = data.cursor_count;
            upgrades.cursor.cost = upgrades.cursor.baseCost * Math.pow(1.15, data.cursor_count);

            upgrades.grandma.count = data.grandma_count;
            upgrades.grandma.cost = upgrades.grandma.baseCost * Math.pow(1.15, data.grandma_count);

            upgrades.factory.count = data.factory_count;
            upgrades.factory.cost = upgrades.factory.baseCost * Math.pow(1.15, data.factory_count);

            recalculateCPS();
            updateUI();
        } else if (response.status === 401) {
            console.warn("Unauthorized! Clearing session and redirecting to login...");
            localStorage.removeItem('primeUser');
            localStorage.removeItem('primeToken');
            window.location.href = '/';
        } else {
            console.error("Failed to load progress from server.");
            updateUI();
        }
    } catch (e) {
        console.error("Connection error loading progress:", e);
        updateUI();
    }
}

async function saveProgress() {
    const user = localStorage.getItem('primeUser');
    if (!user) return;

    const saveData = {
        username: user,
        cookies: cookies,
        totalCookies: totalCookies,
        cps: cps,
        cursor_count: upgrades.cursor.count,
        grandma_count: upgrades.grandma.count,
        factory_count: upgrades.factory.count
    };

    try {
        const token = localStorage.getItem('primeToken') || '';
        await fetch('/save_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(saveData)
        });
    } catch (e) {
        console.error("Connection error saving progress:", e);
    }
}

function formatNumber(num) {
    return Math.floor(num).toLocaleString();
}

function updateUI() {
    cookiesEl.textContent = formatNumber(cookies);
    cpsEl.textContent = cps.toFixed(1);

    Object.keys(upgrades).forEach(key => {
        const upgrade = upgrades[key];
        const card = document.getElementById(`upgrade${key.charAt(0).toUpperCase() + key.slice(1)}`);
        const costEl = document.getElementById(`cost${key.charAt(0).toUpperCase() + key.slice(1)}`);

        costEl.textContent = Math.ceil(upgrade.cost).toLocaleString();

        if (cookies >= upgrade.cost) {
            card.classList.remove('disabled');
        } else {
            card.classList.add('disabled');
        }
    });
}

function setSkin(skins) {
    document.getElementById('bigOrenge').classList.add('active');
    document.getElementById('bigCookie').classList.add('active');
    document.getElementById('bigEgg').classList.add('active');
    document.getElementById('bigCookie').classList.add('active');

    document.getElementById('skins').classList.add('active');
}

bigCookie.addEventListener('mousedown', (e) => {
    cookies += 1;
    totalCookies += 1;

    spawnFloatingText(e.clientX, e.clientY);

    bigCookie.classList.remove('clicked');
    void bigCookie.offsetWidth;
    bigCookie.classList.add('clicked');

    updateUI();
});

function spawnFloatingText(x, y) {
    const floatEl = document.createElement('div');
    floatEl.textContent = '+1';
    floatEl.className = 'plus-one';

    if (!x || !y) {
        const rect = bigCookie.getBoundingClientRect();
        x = rect.left + rect.width / 2;
        y = rect.top + rect.height / 2;
    }

    floatEl.style.left = `${x - 20 + (Math.random() * 40 - 20)}px`;
    floatEl.style.top = `${y - 40}px`;

    document.body.appendChild(floatEl);

    setTimeout(() => {
        floatEl.remove();
    }, 1000);
}

window.buyUpgrade = function (key) {
    const upgrade = upgrades[key];
    const actualCost = Math.ceil(upgrade.cost);

    if (cookies >= actualCost) {
        cookies -= actualCost;
        upgrade.count += 1;
        upgrade.cost = upgrade.baseCost * Math.pow(1.15, upgrade.count);

        recalculateCPS();
        updateUI();
    }
}

function recalculateCPS() {
    let newCps = 0;
    Object.keys(upgrades).forEach(key => {
        newCps += upgrades[key].count * upgrades[key].cpsAdd;
    });
    cps = newCps;
}

setInterval(() => {
    if (cps > 0) {
        cookies += cps / 10;
        totalCookies += cps / 10;
        updateUI();
    }
}, 100);

async function fetchUserRank() {
    const user = localStorage.getItem("primeUser");

    if (!user) return;

    try {
        const response = await fetch(`/get_rank/${user}`);
        console.log(response);
        if (response.ok) {
            const data = await response.json();
            if (data.rank > 0) {
                document.getElementById('userRankDisplay').style.display = 'block';
                document.getElementById('userRank').textContent = `#${data.rank}`;

            }
            const rankEl = document.getElementById("userRank");
            rankEl.textContent = `#${data.rank}`;
        }
    }

    catch
    (e) {
        console.error("Connection error fetching rank:", e);
    }

}

setInterval(() => {
    saveProgress();
    fetchUserRank();
}, 10000);

initUser();
fetchUserRank();

window.logoutUser = async function () {
    try {
        await fetch('/logout', { method: 'POST' });
    } catch (e) {
        console.error("Logout failed:", e);
    }
    localStorage.removeItem('primeUser');
    localStorage.removeItem('primeToken');

    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData) {
        window.Telegram.WebApp.close();
    } else {
        window.location.href = '/';
    }
}


async function checkAndBuySkin(userId, onSuccess) {
  if (!userId) return { ok: false, message: 'userId required' };

  try {
    // 1) получить доступные скины для пользователя
    const availResp = await fetch(`/api/skins/available?user_id=${encodeURIComponent(userId)}`);
    if (!availResp.ok) return { ok: false, message: 'failed to fetch available skins' };
    const available = await availResp.json();

    if (!Array.isArray(available) || available.length === 0) {
      return { ok: false, message: 'no_available_skins' };
    }

    // 2) выбрать один скин (случайный выбор — можно заменить логикой выбора)
    const chosen = available[Math.floor(Math.random() * available.length)];

    // 3) отправить запрос на покупку (обмен печений на скин)
    const buyResp = await fetch('/api/skins/buy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, skin_id: chosen.id })
    });

    // ожидаем JSON ответ вида { ok: bool, message: str, ... }
    const buyResult = await buyResp.json();

    if (buyResp.ok && buyResult.ok) {
      // опционально обновить UI: передать выбранный скин и ответ в callback
      if (typeof onSuccess === 'function') {
        try { onSuccess({ skin: chosen, result: buyResult }); } catch (_) {}
      }
      return { ok: true, skin: chosen, result: buyResult };
    }

    // не хватило печений или другая ошибка
    return { ok: false, message: buyResult.message || 'purchase_failed', result: buyResult };
  } catch (err) {
    return { ok: false, message: err.message || 'unexpected_error' };
  }
}

// Экспорт/доступ в глобальную область, если нужно
if (typeof window !== 'undefined') window.checkAndBuySkin = checkAndBuySkin;

// Listen for storage changes so purchase in another tab updates this page immediately
if (typeof window !== 'undefined') {
    window.addEventListener('storage', (ev) => {
        if (!ev) return;
        if (ev.key === 'primeEquippedSkin') {
            try {
                const v = ev.newValue ? JSON.parse(ev.newValue) : null;
                if (v) {
                    if (v.type) applySkinVisualByType(v.type);
                    else if (v.name) applySkinVisualByName(v.name);
                } else if (!v) {
                     // removed -> reload server state
                     const user = localStorage.getItem('primeUser');
                     if (user) loadAndApplyUserSkin(user).catch(()=>{});
                 }
             } catch (e) {
                 console.warn('storage event parse error', e);
             }
         }
     });
}
