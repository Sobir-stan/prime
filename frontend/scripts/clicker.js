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

// Foydalanuvchini sahifaga kirishi bilan taniy boshlash va ma'lumotlarini yuklash
async function initUser() {
    const urlParams = new URLSearchParams(window.location.search);
    const tgIdParam = urlParams.get('tg_id');
    let tgId = null;

    if (tgIdParam) {
        tgId = parseInt(tgIdParam);
    } else if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
        tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    }

    const activeUser = localStorage.getItem('primeUser');
    const activeToken = localStorage.getItem('primeToken');

    if (tgId && activeUser && activeToken) {
        // Silently bind the Telegram ID to the existing session
        fetch('/link_telegram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${activeToken}`
            },
            body: JSON.stringify({ telegram_id: tgId })
        }).catch(e => console.error("Link error", e));
    } else if (tgId) {
        try {
            window.Telegram.WebApp.expand();
            const resp = await fetch('/tg_login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ telegram_id: tgId })
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
        let finalHash = window.location.hash;
        if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData) {
            finalHash = '#tgWebAppData=' + window.Telegram.WebApp.initData;
        }
        window.location.href = '/' + window.location.search + finalHash;
        return;
    }

    usernameDisplay.textContent = user;
    avatarInitial.textContent = user.charAt(0).toUpperCase();

    await loadProgress(user);
}

// Serverdan progressni (nechta pullari borligi va pechenyelari soni) skachat qilish
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

// Har 10 soniyada progressni serverga (bazaga) doimiy saqlab turish funksiyasi
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

// Katta Cookie ustiga bosilganda chaqiriladigan asosiy o'yin mantiqi (Klyentskiy bosish)
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
    if (cps > 0) {
        cookies += cps / 10;
        totalCookies += cps / 10;
        updateUI();
    }
}, 100);

setInterval(() => {
    saveProgress();
    fetchUserRank();
}, 10000);

initUser();
fetchUserRank();

// Tizimdan chiqish (Logout) hamda brauzer va Telegram xotirasini tozalash funksiyasi
window.logoutUser = async function () {
    try {
        const token = localStorage.getItem('primeToken') || '';
        await fetch('/logout', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
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

let _newsQueue = [];
let _tickerIndex = 0;
let _tickerPlaying = false;
let _currentAnim = null; // reference to current Web Animation so we can cancel when queue changes
let _lastRawNews = null; // serialized localStorage snapshot

async function loadNews() {
    // Try server-first: fetch active news from server endpoint
    let usedServer = false;
    try {
        const resp = await fetch('/news');
        if (resp.ok) {
            const data = await resp.json();
            if (data && Array.isArray(data.news) && data.news.length > 0) {
                // map server items to ticker format
                const list = data.news.map(n => ({ id: n.id, text: n.text, active: true, createdAt: n.created_at }));
                // if queue changed, cancel current animation so new list starts clean
                const serialized = JSON.stringify(list.map(i => i.id + '::' + i.text));
                if (serialized !== _lastRawNews) {
                    try { if (_currentAnim && typeof _currentAnim.cancel === 'function') _currentAnim.cancel(); } catch (e) {}
                    _newsQueue = list.filter(m => m.text && m.text.trim());
                    _lastRawNews = serialized;
                }
                usedServer = true;
            }
        }
    } catch (e) {
        // server may be unreachable; fallback to localStorage below
        // console.warn('Failed to fetch server news:', e);
    }

    if (!usedServer) {
        // Fallback: read from localStorage (admin.html)
        let raw = localStorage.getItem("newsMessages");
        if (!raw) {
            _newsQueue = [];
        } else {
            try {
                const parsed = JSON.parse(raw);
                if (!Array.isArray(parsed) || parsed.length === 0) {
                    _newsQueue = [];
                } else if (typeof parsed[0] === 'string') {
                    // migrate to objects
                    const migrated = parsed.map(s => ({ id: 'm_' + Date.now() + '_' + Math.floor(Math.random()*1000), text: s, active: true, createdAt: new Date().toISOString() }));
                    localStorage.setItem('newsMessages', JSON.stringify(migrated));
                    _newsQueue = migrated.filter(m => m.active);
                } else {
                    // already objects
                    _newsQueue = parsed.map(item => ({ id: item.id || ('m_' + Date.now() + '_' + Math.floor(Math.random()*1000)), text: item.text || '', active: item.active !== false, createdAt: item.createdAt || new Date().toISOString() })).filter(m => m.active && m.text);
                }
            } catch (e) {
                console.error('Failed to parse newsMessages in clicker:', e);
                _newsQueue = [];
            }
        }

        // store serialized snapshot for change detection
        try { _lastRawNews = JSON.stringify(_newsQueue.map(i => i.id + '::' + i.text)); } catch (e) { _lastRawNews = null; }
    }

    // If not currently playing, start the sequential ticker only when there are messages
    if (!_tickerPlaying) {
        _tickerIndex = 0;
        if (_newsQueue.length > 0) playNextNews();
    }
}

function playNextNews() {
    const track = document.querySelector(".news-track");
    if (!_newsQueue || _newsQueue.length === 0) {
        track.innerHTML = '';
        _tickerPlaying = false;
        return;
    }

    _tickerPlaying = true;
    const item = _newsQueue[_tickerIndex % _newsQueue.length];
    const msg = (typeof item === 'string') ? item : (item.text || '');
    if (!msg) {
        // skip empty messages
        _tickerIndex = (_tickerIndex + 1) % _newsQueue.length;
        setTimeout(playNextNews, 100);
        return;
    }

    track.innerHTML = '';
    const span = document.createElement('span');
    span.className = 'single-news';
    span.textContent = msg;

    track.appendChild(span);

    // Measure sizes and animate using Web Animations API so each message
    // starts fully off-screen to the right and moves fully past the left.
    const containerWidth = track.clientWidth;
    const spanWidth = span.offsetWidth;

    // Pixels per second speed (adjustable). Duration computed from distance.
    const pxPerSec = 120; // higher = faster
    const distance = containerWidth + spanWidth;
    const durationMs = Math.max(3000, Math.min(30000, (distance / pxPerSec) * 1000));

    // Place the element just outside the right edge, vertically centered.
    span.style.transform = `translateX(${containerWidth}px) translateY(-50%)`;

    const anim = span.animate([
        { transform: `translateX(${containerWidth}px) translateY(-50%)` },
        { transform: `translateX(${-spanWidth}px) translateY(-50%)` }
    ], {
        duration: durationMs,
        easing: 'linear',
        fill: 'forwards'
    });
    // keep global ref so we can cancel animation if queue changes
    _currentAnim = anim;

    anim.onfinish = () => {
        _currentAnim = null;
        _tickerIndex = (_tickerIndex + 1) % _newsQueue.length;
        span.remove();
        // small delay between messages
        setTimeout(() => {
            // If messages were removed (via storage) and now queue empty, stop
            if (!_newsQueue || _newsQueue.length === 0) {
                track.innerHTML = '';
                _tickerPlaying = false;
                return;
            }
            playNextNews();
        }, 300);
    };
}

function addNewsMessage(msg) {
    if (!msg) return;
    msg = msg.toString().trim();
    if (msg.length === 0) return;

    // Save locally so the ticker updates immediately (store as objects)
    const raw = JSON.parse(localStorage.getItem("newsMessages")) || [];
    const toPush = { id: 'm_' + Date.now() + '_' + Math.floor(Math.random()*1000), text: msg, active: true, createdAt: new Date().toISOString() };
    raw.push(toPush);
    localStorage.setItem("newsMessages", JSON.stringify(raw));

    // Try to send to server (if your Java backend exposes /add_news). Failure is non-fatal.
    try {
        const token = localStorage.getItem('primeToken') || '';
        fetch('/add_news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ message: msg })
        }).catch(e => console.warn('Failed to POST news to server:', e));
    } catch (e) {
        console.warn('Error while posting news:', e);
    }

    loadNews();
}

// React to storage changes from admin page
window.addEventListener('storage', function(e) {
    if (e.key === 'newsMessages') {
        loadNews();
    }
});

// Wire up controls (works whether script is loaded at end or earlier)
function wireNewsControls() {
    const input = document.getElementById('newsInput');
    const btn = document.getElementById('newsAddBtn');
    if (!input || !btn) return;

    btn.addEventListener('click', () => {
        addNewsMessage(input.value);
        input.value = '';
        input.focus();
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            addNewsMessage(input.value);
            input.value = '';
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { wireNewsControls(); loadNews(); });
} else {
    wireNewsControls();
    loadNews();
}

// Poll server for news changes every 5 seconds (for environments where storage event may not fire)
setInterval(() => {
    loadNews();
}, 5000);

