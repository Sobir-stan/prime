// Barcha promokodlarni ma'lumotlar bazasidan o'qib kelish va HTML ro'yxatga chiqarish
async function fetchPromos() {
    const res = await fetch('/admin/promocodes');
    if (res.ok) {
        const promos = await res.json();
        const list = document.getElementById('promoList');
        list.innerHTML = '';
        promos.forEach(p => {
            const li = document.createElement('li');
            li.style.marginBottom = '10px';
            li.style.padding = '10px';
            li.style.background = '#f9f9f9';
            li.style.border = '1px solid #ddd';
            li.style.borderRadius = '5px';
            li.innerHTML = `
                <strong>${p.code}</strong> - 🍪 ${p.reward} pechenye <br>
                <small>Ishlatildi: ${p.current_uses} marta (Limit: ${p.max_uses === 0 ? 'Cheksiz' : p.max_uses})</small><br>
                <button onclick="togglePromo(${p.id}, ${!p.is_active})" style="margin-top: 8px; cursor: pointer; padding: 5px 10px; border:none; border-radius: 4px; font-size: 0.85em; background: ${p.is_active ? '#c0392b' : '#27ae60'}; color: white;">
                    ${p.is_active ? 'Faolsizlantirish' : 'Faollashtirish'}
                </button>
            `;
            list.appendChild(li);
        });
    }
}

// Yangi promokod yaratish. Forma ma'lumotlari backendga jo'natiladi
async function createPromo() {
    const code = document.getElementById('promoCode').value.trim();
    const reward = parseFloat(document.getElementById('promoReward').value);
    const max_uses = parseInt(document.getElementById('promoUses').value || 0);

    if (!code || isNaN(reward)) return alert("Promokod nomi va miqdori albatta ko'rsatilishi shart!");

    const res = await fetch('/admin/promocodes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, reward, max_uses, is_active: true })
    });

    const data = await res.json();
    alert(data.msg || data.detail);

    if (res.ok) {
        document.getElementById('promoCode').value = '';
        document.getElementById('promoReward').value = '';
        document.getElementById('promoUses').value = '';
        fetchPromos();
    }
}

// Promokodning holatini (faol yoki nofaol) o'zgartirish
async function togglePromo(id, newState) {
    const res = await fetch(`/admin/promocodes/${id}/toggle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: newState })
    });
    if (res.ok) fetchPromos();
}

// Sahifa yuklanishi bilan bazadagi kodlarni ro'yxatini yuklash
fetchPromos();
