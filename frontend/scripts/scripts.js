async function registerUser() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const errorMsg = document.getElementById('password-error');

    if (!username || !email || !password || !confirmPassword) {
        alert("Iltimos hammasini to'ldiring.");
        return;
    }

    if (password !== confirmPassword) {
        errorMsg.style.display = 'block';
        return;
    } else {
        errorMsg.style.display = 'none';
    }

    const data = {
        username: username,
        email: email,
        password: password
    };

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            alert("Registration successful: " + JSON.stringify(result));

        } else {
            alert("Registration failed. Status: " + response.status);
        }
    } catch (error) {
        console.error('Error:', error);
        alert("An error occurred during registration.");
    }
}