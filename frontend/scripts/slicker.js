// slicker.js — функция для проверки доступных скинов и автоматической покупки
// Функции:
// - fetchAvailableSkins(userId): получает список доступных (не купленных) скинов
// - tryAutoBuySkin(userId, onSuccess): если есть доступный скин и хватает печенек на сервере — покупает
// - fetchSkinSummary(userId): получает summary (owned, available, cookies, affordable_ids)
// - buySpecificSkin(userId, skinId): пытается купить конкретный skin_id

async function fetchAvailableSkins(userId) {
  if (!userId) throw new Error('userId required');
  const resp = await fetch(`/api/skins/available?user_id=${encodeURIComponent(userId)}`);
  if (!resp.ok) throw new Error('Failed to fetch available skins');
  return await resp.json();
}

async function fetchSkinSummary(userId) {
  if (!userId) throw new Error('userId required');
  const resp = await fetch(`/api/skins/summary?user_id=${encodeURIComponent(userId)}`);
  if (!resp.ok) throw new Error('Failed to fetch skin summary');
  return await resp.json();
}

async function buySpecificSkin(userId, skinId) {
  if (!userId) return { ok: false, message: 'userId required' };
  if (!skinId && skinId !== 0) return { ok: false, message: 'skinId required' };

  try {
    const token = localStorage.getItem('primeToken') || '';
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const buyResp = await fetch('/api/skins/buy', {
      method: 'POST',
      headers,
      body: JSON.stringify({ user_id: userId, skin_id: Number(skinId) })
    });

    // If server responds with non-2xx, try to parse message or throw
    if (!buyResp.ok) {
      let errMsg = 'purchase_failed';
      try {
        const errJson = await buyResp.json();
        errMsg = errJson.detail || errJson.message || errJson.error || errMsg;
      } catch(_) {}
      return { ok: false, message: errMsg, status: buyResp.status };
    }

    const buyResult = await buyResp.json();
    if (buyResult.ok) {
      if (buyResult.skin) {
        try { localStorage.setItem('primeEquippedSkin', JSON.stringify(buyResult.skin)); } catch(_) {}
      }
      return { ok: true, result: buyResult, skin: buyResult.skin || null };
    }
    return { ok: false, message: buyResult.message || 'purchase_failed', result: buyResult };
  } catch (err) {
    return { ok: false, message: err.message || 'unexpected_error' };
  }
}

async function tryAutoBuySkin(userId, onSuccess) {
  if (!userId) return { ok: false, message: 'userId required' };

  try {
    const summary = await fetchSkinSummary(userId);
    if (!summary || !Array.isArray(summary.available) || summary.available.length === 0) {
      return { ok: false, message: 'no_available_skins' };
    }

    // try to pick an affordable skin first
    let chosen = null;
    if (Array.isArray(summary.affordable_ids) && summary.affordable_ids.length > 0) {
      const affordable = summary.available.filter(s => summary.affordable_ids.includes(s.id));
      if (affordable.length > 0) chosen = affordable[0];
    }
    // fallback to first available
    if (!chosen) chosen = summary.available[0];

    const buyResp = await buySpecificSkin(userId, chosen.id);
    if (buyResp.ok) {
      if (typeof onSuccess === 'function') {
        try { onSuccess({ skin: chosen, result: buyResp.result }); } catch(_) {}
      }
      return { ok: true, skin: chosen, result: buyResp.result };
    }

    return { ok: false, message: buyResp.message || 'purchase_failed', result: buyResp.result };
  } catch (err) {
    return { ok: false, message: err.message || 'unexpected_error' };
  }
}

if (typeof window !== 'undefined') {
  window.fetchAvailableSkins = fetchAvailableSkins;
  window.tryAutoBuySkin = tryAutoBuySkin;
  window.fetchSkinSummary = fetchSkinSummary;
  window.buySpecificSkin = buySpecificSkin;
}

export { fetchAvailableSkins, tryAutoBuySkin, fetchSkinSummary, buySpecificSkin };
