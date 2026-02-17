import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  RecaptchaVerifier,
  signInWithPhoneNumber
} from "https://www.gstatic.com/firebasejs/11.0.0/firebase-auth.js";
async function fetchFirebaseConfig() {
  const response = await fetch('/api/get_firebase_config');
  return await response.json();
}
const app = initializeApp(await fetchFirebaseConfig());
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const googleBtn = document.getElementById("google-login-btn");

if (googleBtn) {
  googleBtn.addEventListener("click", async (e) => {
    e.preventDefault(); 
    try {
      // 1) Google popup
      const result = await signInWithPopup(auth, provider);
      const user = result.user;

      // 2) Get ID token
      const idToken = await user.getIdToken();

      // 3) Send token to Python backend
      const response = await fetch("/google-login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idToken: idToken }),
      });

      if (response.ok) {
        // backend created session, now go to dashboard
        window.location.href = "/";
      } else {
        const data = await response.json();
        alert("Server error: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      console.error(err);
      alert("Google login failed");
    }
  });
}
// ---------- SIGN UP ----------
const signupForm = document.getElementById("emailSignUpForm");

if (signupForm) {
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("nameSignUpInput").value;
    const email = document.getElementById("emailSignUpInput").value;
    const password = document.getElementById("passwordSignUpInput").value;
    const confirmPassword = document.getElementById("confirmPasswordSignUpInput").value;

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    try {
      // 1) Ask Firebase to create user + store password securely
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      const user = cred.user;

      // 2) Get ID token from Firebase
      const idToken = await user.getIdToken();

      // 3) Tell Flask: “this is the logged-in user”
      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idToken: idToken ,
            name: name
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        alert("Server error (signup): " + (data.error || "Unknown error"));
        return;
      }

      // 4) Backend created session → go to dashboard/home
      window.location.href = "/";
    } catch (err) {
      console.error(err);
      alert("Signup failed: " + err.message);
    }
  });
}

// ---------- LOGIN ----------
const signinForm = document.getElementById("emailSignInForm");

if (signinForm) {
  signinForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("emailSignInInput").value;
    const password = document.getElementById("passwordSignInInput").value;

    try {
      // 1) Ask Firebase to check email + password
      const cred = await signInWithEmailAndPassword(auth, email, password);
      const user = cred.user;

      // 2) Get ID token
      const idToken = await user.getIdToken();

      // 3) Send token to backend
      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idToken }),
      });

      if (!res.ok) {
        const data = await res.json();
        alert("Server error (signin): " + (data.error || "Unknown error"));
        return;
      }

      // 4) Session created → redirect
      window.location.href = "/";
    } catch (err) {
      console.error(err);
      alert("signin failed: " + err.message);
    }
  });
}
// ================= PHONE LOGIN =================

window.recaptchaVerifier = new RecaptchaVerifier(auth, "recaptcha-container", {
  size: "normal"
});

const sendOtpBtn = document.getElementById("send-otp");
const verifyOtpBtn = document.getElementById("verify-otp");

let confirmationResult = null;

// SEND OTP
if (sendOtpBtn) {
  sendOtpBtn.addEventListener("click", async () => {
    const phone = document.getElementById("phone").value;

    try {
      confirmationResult = await signInWithPhoneNumber(
        auth,
        phone,
        window.recaptchaVerifier
      );

      alert("OTP sent!");
    } catch (err) {
      console.error(err);
      alert("OTP failed: " + err.message);
    }
  });
}

// VERIFY OTP
if (verifyOtpBtn) {
  verifyOtpBtn.addEventListener("click", async () => {
    const otp = document.getElementById("otp").value;

    try {
      const result = await confirmationResult.confirm(otp);
      const user = result.user;

      const idToken = await user.getIdToken();

      // send to Flask
      const res = await fetch("/phone-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idToken: idToken }),
      });

      if (res.ok) {
        window.location.href = "/";
      } else {
        alert("Backend error");
      }
    } catch (err) {
      console.error(err);
      alert("Invalid OTP");
    }
  });
}
