let cookies = 0;
let totalCookies = 0;
let cps = 0;

// Upgrades Data
const upgrades = {
    cursor: { baseCost: 15, cost: 15, count: 0, cpsAdd: 0.1 },
    grandma: { baseCost: 100, cost: 100, count: 0, cpsAdd: 1 },
    factory: { baseCost: 1000, cost: 1000, count: 0, cpsAdd: 8 }
};

// DOM Elements
const cookiesEl = document.getElementById('cookies');
const cpsEl = document.getElementById('cps');
const bigCookie = document.getElementById('bigCookie');
const usernameDisplay = document.getElementById('usernameDisplay');
const avatarInitial = document.getElementById('avatarInitial');

// Initialize User
function initUser() {
    // Attempt to get user info from localStorage or session, placeholder for now
    // Actually, in login.js we can set localStorage on successful login.
    const user = localStorage.getItem('primeUser') || "Player 1";
    usernameDisplay.textContent = user;
    avatarInitial.textContent = user.charAt(0).toUpperCase();
}

// Format numbers securely
function formatNumber(num) {
    return Math.floor(num).toLocaleString();
}

// Update UI
function updateUI() {
    cookiesEl.textContent = formatNumber(cookies);
    cpsEl.textContent = cps.toFixed(1);

    // Update Store Buttons
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

// Click the Big Cookie
bigCookie.addEventListener('mousedown', (e) => {
    // Add point
    cookies += 1;
    totalCookies += 1;

    // Spawn +1 text
    spawnFloatingText(e.clientX, e.clientY);

    // Trigger CSS animation manually so it works every click
    bigCookie.classList.remove('clicked');
    void bigCookie.offsetWidth; // Trigger reflow to restart animation
    bigCookie.classList.add('clicked');

    // Update UI immediately for responsiveness
    updateUI();
});

// Floating Text Animation function
function spawnFloatingText(x, y) {
    const floatEl = document.createElement('div');
    floatEl.textContent = '+1';
    floatEl.className = 'plus-one';

    // Adjust starting position if triggered programmatically
    if (!x || !y) {
        const rect = bigCookie.getBoundingClientRect();
        x = rect.left + rect.width / 2;
        y = rect.top + rect.height / 2;
    }

    // Center it somewhat randomly on the cursor
    floatEl.style.left = `${x - 20 + (Math.random() * 40 - 20)}px`;
    floatEl.style.top = `${y - 40}px`;

    document.body.appendChild(floatEl);

    // Remove element after animation
    setTimeout(() => {
        floatEl.remove();
    }, 1000);
}

// Buy Upgrade Function
// Expose functions explicitly so inline onclick calls them appropriately.
window.buyUpgrade = function (key) {
    const upgrade = upgrades[key];
    const actualCost = Math.ceil(upgrade.cost);

    if (cookies >= actualCost) {
        cookies -= actualCost;
        upgrade.count += 1;
        // Increase Cost by 15% each time
        upgrade.cost = upgrade.baseCost * Math.pow(1.15, upgrade.count);

        // Recalculate CPS
        recalculateCPS();
        updateUI();
    }
}

// Recalculate CPS
function recalculateCPS() {
    let newCps = 0;
    Object.keys(upgrades).forEach(key => {
        newCps += upgrades[key].count * upgrades[key].cpsAdd;
    });
    cps = newCps;
}

// Game Loop for CPS (runs 10 times a second)
setInterval(() => {
    if (cps > 0) {
        // Add 1/10th of the CPS every 100ms
        cookies += cps / 10;
        totalCookies += cps / 10;
        updateUI();
    }
}, 100);

// Initialize game
initUser();
updateUI();
