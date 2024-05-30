function validatelogin() {
    if (loginuser() && loginuserlocalstorage()) {
        return true;
    } else {
        return false; // At least one function returned false, so prevent form submission
    }
}

function validateregister() {
    if (registeruser() && registeruserlocalstorage()) {
        return true; // Both functions returned true, so allow form submission
    } else {
        return false; // At least one function returned false, so prevent form submission
    }
}

function loginuser() {
    var username = document.getElementById("login-username").value;
    var password = document.getElementById("login-password").value;

    if (username.trim() === "" || password.trim() === "") {
        alert("💥 Username or email cannot be blank. Please enter valid username or email.");
        return false;
    }

    return true;
}

function registeruser() {
    var firstName = document.getElementById("register-username").value;
    var lastName = document.getElementById("last-name").value;
    var email = document.getElementById("register-email").value;
    var password = document.getElementById("register-password").value;

    if (firstName.trim() === "") {
        alert("💥 Firstname cannot be empty.");
        return false;
    }

    if (lastName.trim() === "") {
        alert("💥 Lastname cannot be empty.");
        return false;
    }

    if (email.trim() === "") {
        alert("💥 Please enter a valid email address.");
        return false;
    }

    // Simple email validation regex
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert("💥 Please enter a valid email address.");
        return false;
    }

    // Simple password strength check (at least 6 characters)
    if (password.length < 6) {
        alert("💥 Password should be at least 6 characters long.");
        return false;
    }

    return true;
}

// Function to register a new user
function registeruserlocalstorage() {
    var username = document.getElementById('register-username').value;
    var password = document.getElementById('register-password').value;
    // Add other registration details as needed

    // Store the registration data in localStorage
    localStorage.setItem('username', username);
    localStorage.setItem('password', password);
    // You can store other registration details similarly

    alert('Registration successful!');
}

// Function to perform login authentication
function loginuserlocalstorage() {
    var storedUsername = localStorage.getItem('username');
    var storedPassword = localStorage.getItem('password');

    var enteredUsername = document.getElementById('login-username').value;
    var enteredPassword = document.getElementById('login-password').value;

    if (storedUsername === enteredUsername && storedPassword === enteredPassword) {
        // Redirect the user to the website or perform any other action for successful login
        alert('Login successful! Redirecting...');
        document.getElementById("welcomeBtn").disabled = false;
        //window.location.href = 'index.html'; // Redirect to a welcome page
    } else {
        // Display error message for incorrect credentials
        alert('No such user exists or incorrect password.');
    }
}

function requesttime(){
    var storedPassword = localStorage.getItem('password');
    var enteredPassword = document.getElementById('check-password').value;

    if (storedPassword === enteredPassword) {
        // Redirect the user to the website or perform any other action for successful login
        alert('password verified successfully..');
        return true;
    } else {
        // Display error message for incorrect credentials
        alert(' incorrect password.');
        return false;
    }

}