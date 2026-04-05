document.addEventListener("DOMContentLoaded", () => {
    const activeUser = localStorage.getItem('primeUser');
    const activeToken = localStorage.getItem('primeToken');
    if (activeUser && activeToken) {
        window.location.href = '/clicker' + window.location.search;
    }
});

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
                window.location.href = '/';
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
