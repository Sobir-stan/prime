let cookies = 0;
let totalCookies = 0;
let cps = 0;
let cookiesAtLastSave = 0; // Authoritative cookie count from the last successful save/load

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

// This is the new, robust, non-destructive state-merging logic
window.addEventListener('focus', async () => {
    const user = localStorage.getItem('primeUser');
    if (!user) return;

    console.log("Window focused. Syncing state with server...");
    try {
        const token = localStorage.getItem('primeToken') || '';
        const response = await fetch(`/load_progress/${user}`, { headers: { 'Authorization': `Bearer ${token}` } });
        
        if (response.ok) {
            const serverProgress = await response.json();
            
            // Calculate the cookies earned locally since the last time we synced with the server
            const unsavedDelta = cookies - cookiesAtLastSave;
            
            // The new authoritative state is the server's state plus our unsaved local progress
            const newAuthoritativeCookies = serverProgress.cookies + unsavedDelta;

            if (Math.floor(cookies) !== Math.floor(newAuthoritativeCookies)) {
                console.log("Server state has changed. Merging states.");
                cookies = newAuthoritativeCookies;
                totalCookies = serverProgress.totalCookies + (unsavedDelta > 0 ? unsavedDelta : 0);
                
                // Update the baseline for the next save/sync to the new merged state
                cookiesAtLastSave = newAuthoritativeCookies;
                
                updateUI();
            } else {
                console.log("States are in sync.");
            }
        }
    } catch (e) {
        console.error("Error syncing progress on focus:", e);
    }
});

async function initUser() {
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
        const tgUser = window.Telegram.WebApp.initDataUnsafe.user;
        const tgId = tgUser.id;
        const tgUsername = tgUser.username || `user_${tgId}`;
        try {
            window.Telegram.WebApp.expand();
            const checkResp = await fetch(`/check_telegram_user/${tgId}`);
            const checkData = await checkResp.json();
            if (!checkData.exists) {
                window.location.href = `/register?tg_id=${tgId}`;
                return;
            }
            const resp = await fetch('/tg_login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ telegram_id: tgId, username: checkData.username })
            });
            if (resp.ok) {
                const data = await resp.json();
                localStorage.setItem('primeUser', data.username);
                if (data.token) localStorage.setItem('primeToken', data.token);
            }
        } catch (e) { console.error("TG Auth error", e); }
    }
    const user = localStorage.getItem('primeUser');
    if (!user) {
        window.location.href = '/';
        return;
    }
    usernameDisplay.textContent = user;
    avatarInitial.textContent = user.charAt(0).toUpperCase();
    await loadProgress(user);
}

async function loadProgress(username) {
    try {
        const token = localStorage.getItem('primeToken') || '';
        const response = await fetch(`/load_progress/${username}`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (response.ok) {
            const data = await response.json();
            cookies = data.cookies;
            totalCookies = data.totalCookies;
            cookiesAtLastSave = data.cookies; // Set the baseline for delta calculation
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
    } catch (e) { console.error("Connection error loading progress:", e); }
}

async function saveProgress() {
    const user = localStorage.getItem('primeUser');
    if (!user) return;

    const cookie_delta = cookies - cookiesAtLastSave;
    
    const saveData = {
        username: user,
        cookie_delta: cookie_delta,
        cps: cps,
        cursor_count: upgrades.cursor.count,
        grandma_count: upgrades.grandma.count,
        factory_count: upgrades.factory.count
    };

    try {
        const token = localStorage.getItem('primeToken') || '';
        const response = await fetch('/save_progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(saveData)
        });

        if (response.ok) {
            cookiesAtLastSave = cookies;
        } else {
            console.error("Save failed with status:", response.status, await response.text());
        }
    } catch (e) {
        console.error("Connection error saving progress:", e);
    }
}

function formatNumber(num) { return Math.floor(num).toLocaleString(); }

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

bigCookie.addEventListener('mousedown', (e) => {
    cookies += 1;
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
    setTimeout(() => { floatEl.remove(); }, 1000);
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
        cookies += (cps / 10);
        updateUI();
    }
}, 100);

async function fetchUserRank() {
    const user = localStorage.getItem("primeUser");
    if (!user) return;
    try {
        const token = localStorage.getItem('primeToken') || '';
        const response = await fetch(`/get_rank`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (response.ok) {
            const data = await response.json();
            if (data.rank > 0) {
                document.getElementById('userRankDisplay').style.display = 'block';
                document.getElementById('userRank').textContent = `#${data.rank}`;
            }
        }
    } catch (e) { console.error("Connection error fetching rank:", e); }
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
    } catch (e) { console.error("Logout failed:", e); }
    localStorage.removeItem('primeUser');
    localStorage.removeItem('primeToken');
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData) {
        window.Telegram.WebApp.close();
    } else {
        window.location.href = '/';
    }
}

window.openPromoModal = function () { document.getElementById('promoModal').style.display = 'flex'; }
window.closePromoModal = function () { document.getElementById('promoModal').style.display = 'none'; document.getElementById('promoCode').value = ''; }

window.applyPromo = async function () {
    const code = document.getElementById('promoCode').value.trim();
    if (!code) {
        alert('Iltimos, promo kod kiriting.');
        return;
    }
    try {
        const token = localStorage.getItem('primeToken') || '';
        const response = await fetch('/apply_promo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ code: code })
        });
        const data = await response.json();
        alert(data.message || data.detail);
        if (response.ok && data.success) {
            closePromoModal();
            location.reload();
        }
    } catch (e) {
        console.error('Promo apply error:', e);
        alert('Xatolik yuz berdi.');
    }
}
