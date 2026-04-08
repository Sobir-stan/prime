// Brauzer to'liq yuklangandan so'ng, tizimga avval kiritilgan tokenni tekshiradi
// Agar foydalanuvchi joriy qurilmada oldin login qilgan bo'lsa, to'g'ridan to'g'ri o'yinga yo'naltiriladi
document.addEventListener("DOMContentLoaded", () => {
    const activeUser = localStorage.getItem('primeUser');
    const activeToken = localStorage.getItem('primeToken');
    if (activeUser && activeToken) {
        window.location.href = '/clicker' + window.location.search;
    }
});

// Foydalanuvchi kiritgan ma'lumotlar bilan tizimga kirish (Login) jarayoni
async function loginUser() {
    const username = document.getElementById('login_username')?.value;
    const password = document.getElementById('login_password')?.value;

    console.log(`[Login Attempt] Username: ${username}`);

    if (!username || !password) {
        const msg = "Iltimos barcha maydonlarni to'ldiring. (Please fill all fields)";
        console.warn(`[Login Error] Validation failed: ${msg}`);
        showNotification(msg, 'error');
        return;
    }

    const data = {
        username: username,
        password: password
    };

    // Agar manzil satrida Telegram ID bo'lsa (URL qismida) yoki WebApp orqali kirgan bo'lsa
    // Uni serverga biriktirish uchun aniqlaymiz
    const urlParams = new URLSearchParams(window.location.search);
    const tgIdParam = urlParams.get('tg_id');

    if (tgIdParam) {
        data.telegram_id = parseInt(tgIdParam);
    } else if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
        data.telegram_id = window.Telegram.WebApp.initDataUnsafe.user.id;
    }



    try {
        console.log(`[Login Request] Sending POST to /login...`, data);
        const response = await fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            showNotification("Kirish muvaffaqiyatli! O'yinga yo'naltirilmoqdasiz...", 'success');

            // Avtorizatsiya ma'lumotlari mahalliy xotirada saqlanadi
            localStorage.setItem('primeUser', username);
            if (result.token) localStorage.setItem('primeToken', result.token);

            // O'yinga kirish
            setTimeout(() => {
                window.location.href = '/clicker';
            }, 500);
        } else {
            console.error(`[Login Error] Server returned status ${response.status} ${response.statusText}`);
            try {
                const errorData = await response.json();
                console.error(`[Login Error Data]`, errorData);
                showNotification(errorData.detail || "Noto'g'ri ism yoki parol kiritildi. (Invalid credentials)", 'error');
            } catch (jsonErr) {
                showNotification("Noto'g'ri ism yoki parol kiritildi.", 'error');
            }
        }
    } catch (error) {
        console.error('[Login Exception] Request failed to complete:', error);
        showNotification("Kirish paytida server bilan xatolik yuz berdi. (Server connection error)", 'error');
    }
}

function forgotPassword() {
    showNotification("Parolni tiklash funksiyasi hali ishga tushirilmadi. (Forgot password not implemented)", 'error');
}
