
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

async function registerUser() {
    const username = document.getElementById('username')?.value;
    const email = document.getElementById('email')?.value;
    const password = document.getElementById('password')?.value;
    const confirmPassword = document.getElementById('confirm_password')?.value;

    console.log(`[Register Attempt] Username: ${username}, Email: ${email}`);

    if (!username || !email || !password || !confirmPassword) {
        const msg = "Iltimos hammasini to'ldiring. (Please fill all fields)";
        console.warn(`[Register Error] Validation failed: ${msg}`);
        showNotification(msg, 'error');
        return;
    }

    if (password !== confirmPassword) {
        const msg = "Parol bir xil emas. (Passwords do not match)";
        console.warn(`[Register Error] Validation failed: ${msg}`);
        showNotification(msg, 'error');
        return;
    }

    const data = {
        username: username,
        email: email,
        password: password
    };

    try {
        console.log(`[Register Request] Sending POST to /register...`, data);
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            console.log(`[Register Success] Server responded:`, result);
            showNotification("Ro'yxatdan o'tish muvaffaqiyatli! (Registration successful)", 'success');


            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        } else {
            console.error(`[Register Error] Server returned status ${response.status} ${response.statusText}`);
            try {
                const errorData = await response.json();
                console.error(`[Register Error Data]`, errorData);
                showNotification(`Ro'yxatdan o'tishda xatolik: ${errorData.detail || response.statusText}`, 'error');
            } catch (jsonErr) {
                showNotification(`Ro'yxatdan o'tishda xatolik: ${response.status}`, 'error');
            }
        }
    } catch (error) {
        console.error('[Register Exception] Request failed to complete:', error);
        showNotification("Server bilan ulanishda xatolik yuz berdi. (Connection error)", 'error');
    }
}

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
            console.log(`[Login Success] Server responded:`, result);
            showNotification("Kirish muvaffaqiyatli! (Login successful)", 'success');

            localStorage.setItem('primeUser', username);
            if (result.token) localStorage.setItem('primeToken', result.token);
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