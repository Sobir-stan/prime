document.addEventListener('DOMContentLoaded', () => {
    fetchRating();
});

async function fetchRating() {
    const tbody = document.getElementById('rating-body');
    const loading = document.getElementById('loading');

    try {
        const response = await fetch('/get_rating');
        if (!response.ok) {
            throw new Error('Reytingni olishda xatolik');
        }

        const data = await response.json();

        loading.style.display = 'none';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 3rem; color: #9ca3af;">Hozircha o\'yinchilar yo\'q.</td></tr>';
            return;
        }

        tbody.innerHTML = '';

        data.forEach((player, index) => {
            const tr = document.createElement('tr');

            const initial = player.username ? player.username.charAt(0).toUpperCase() : '?';
            const totalCookies = Math.floor(player.totalCookies || 0).toLocaleString();
            const cps = (player.cps || 0).toFixed(1);


            let rankHtml = `#${index + 1}`;
            if (index === 0) rankHtml = `👑 1`;
            if (index === 1) rankHtml = `🥈 2`;
            if (index === 2) rankHtml = `🥉 3`;

            tr.innerHTML = `
                <td class="rank">${rankHtml}</td>
                <td>
                    <div class="user-info">
                        <div class="user-avatar">${initial}</div>
                        <span class="user-name">${player.username || 'Noma\'lum'}</span>
                    </div>
                </td>
                <td class="score">${totalCookies} 🍪</td>
                <td class="cps">${cps}/s</td>
            `;

            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error('Error:', error);
        loading.className = 'error';
        loading.textContent = 'Ma\'lumotlarni yuklashda xatolik yuz berdi. Iltimos qaytadan urinib ko\'ring.';
    }
}
