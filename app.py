from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from services import firebase_services
from firebase_admin import auth
import os
app = Flask(__name__)
app.secret_key = "super-secret-key"


# ======================
# Helpers
# ======================

# ======================
# Public Pages
# ======================

@app.route("/")
def landing():
    return render_template("home.html",user=session["user"])

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/api/get_firebase_config", methods=['GET'])
def get_firebase_config():
    firebase_config = {
        "apiKey": os.environ.get("FIREBASE_API_KEY"),
        "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
        "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.environ.get("FIREBASE_APP_ID"),
        "vapidKey": os.environ.get("FIREBASE_VAPID_KEY")
    }
    return jsonify(firebase_config)
@app.route("/getstarted")
def getstarted():
    return render_template("getstarted.html")


@app.route('/login')
def login():
    data = request.get_json()
    id_token = data.get("idToken")

    if not id_token:
        return jsonify({"success": False, "error": "Missing token"}), 400

    try:
        decoded = auth.verify_id_token(id_token)
    except Exception as e:
        print("Token verification error:", e)
        return jsonify({"success": False, "error": "Invalid token"}), 401

    email = decoded.get("email")
    name = decoded.get("name") or email.split("@")[0] or data.get("name", "User")
    uid = decoded.get("uid")

    # Check / create user document in Firestore (no password)
    user_data = firebase_service.get_user_by_uid(uid)
    photo=decoded.get("picture", "https://ik.imagekit.io/RemediRX/pngwing.com.png?updatedAt=1764494288724")
    if not user_data:
        firebase_service.add_user(uid=uid,email=email,name=name,photo_url=photo)
        user_data = {"uid": uid, "name": name, "photo_url":photo,"fcm_enabled": False}

    session.permanent = True
    session["user"] = user_data
    return jsonify({"success": True})



@app.route("/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    id_token = data.get("idToken")

    if not id_token:
        return jsonify({"success": False, "error": "Missing token"}), 400

    try:
        decoded = auth.verify_id_token(id_token)
    except Exception as e:
        print("Token verification error:", e)
        return jsonify({"success": False, "error": "Invalid token"}), 401
    uid= decoded.get("uid")
    email = decoded.get("email")
    name = decoded.get("name") or email.split("@")[0]

    # Check if user exists in Firestore; if not, create
    user_data = firebase_service.get_user_by_uid(uid)
    if not user_data:
        photo=decoded.get("picture", "https://ik.imagekit.io/RemediRX/pngwing.com.png?updatedAt=1764494288724")
        firebase_service.add_user(uid=uid,email=email,name=name,photo_url=photo)
        user_data = {"uid": uid, "name": name, "photo_url": photo,"fcm_enabled": False}

    session.permanent = True
    session["user"] = user_data    

    return jsonify({"success": True})

@app.route("/phone-login", methods=["POST"])
def phone_login():
    data = request.get_json()
    id_token = data.get("idToken")

    if not id_token:
        return jsonify({"success": False, "error": "Missing token"}), 400

    try:
        decoded = auth.verify_id_token(id_token)
    except Exception as e:
        print("Token verification error:", e)
        return jsonify({"success": False, "error": "Invalid token"}), 401

    uid = decoded.get("uid")
    phone = decoded.get("phone_number")   # <-- phone comes here
    name = decoded.get("name") or "User"

    # fallback photo
    photo = decoded.get(
        "picture",
        "https://ik.imagekit.io/RemediRX/pngwing.com.png?updatedAt=1764494288724"
    )

    # IMPORTANT: use UID or phone as lookup key
    user_data = firebase_service.get_user_by_uid(uid)

    if not user_data:
        firebase_service.add_user_phone(
            uid=uid,
            phone=phone,
            name=name,
            photo_url=photo
        )

        user_data = {
            "uid": uid,
            "name": name,
            "photo_url": photo,
            "fcm_enabled": False
        }

    session.permanent = True
    session["user"] = user_data

    return jsonify({"success": True})

@app.route("/api/update-profile", methods=["POST"])
def update_profile():

    if "user" not in session:
        return {"success": False}, 401

    uid = session["user"]["uid"]
    data = request.get_json()
    firebase_service.update_user_profile(uid, data)

    return {"success": True}

@app.route("/profile/<slug>")
def worker_profile(slug):
    return render_template("worker_profile.html", slug=slug)

# ======================
# Firebase Login Handler
# ======================

@app.route("/firebase-login", methods=["POST"])
def firebase_login():

    id_token = request.json.get("idToken")

    decoded = auth.verify_id_token(id_token)
    uid = decoded["uid"]

    user_ref = db.collection("users").document(uid).get()

    if user_ref.exists:
        role = user_ref.to_dict()["role"]
    else:
        role = None

    session["uid"] = uid
    session["role"] = role

    return {"status": "ok", "role": role}

# ======================
# Role Setup (First Time)
# ======================

@app.route("/select-role", methods=["POST"])
def select_role():

    role = request.form.get("role")
    uid = session["uid"]

    db.collection("users").document(uid).set({
        "role": role
    })

    session["role"] = role

    if role == "worker":
        return redirect("/worker/dashboard")
    else:
        return redirect("/customer/dashboard")

# ======================
# Dashboards
# ======================

@app.route("/worker/dashboard")
def worker_dashboard():
    check = login_required("worker")
    if check: return check
    return render_template("worker_dashboard.html")

@app.route("/customer/dashboard")
def customer_dashboard():
    check = login_required("customer")
    if check: return check
    return render_template("customer_dashboard.html")

# ======================
# Logout
# ======================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ======================
# Error
# ======================

@app.errorhandler(403)
def forbidden(e):
    return "Forbidden", 403

# ======================
# Run
# ======================

if __name__ == "__main__":
    app.run(debug=True)
