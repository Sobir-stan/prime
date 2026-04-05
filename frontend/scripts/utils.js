function showNotification(message, type = 'error') {
    const notifEl = document.getElementById('global-notification');

    if (!notifEl) {
        console.warn('UI Notification container not found for:', message);
        alert(message);
        return;
    }

    notifEl.textContent = message;
    notifEl.className = type === 'error' ? 'error-msg' : 'success-msg';
    notifEl.style.display = 'block';
    notifEl.style.opacity = '1';


    setTimeout(() => {
        notifEl.style.opacity = '0';
        setTimeout(() => notifEl.style.display = 'none', 300);
    }, 5000);
}
