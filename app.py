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
    return render_template("home.html",user=session.get("user"))

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

@app.route("/firebase-login", methods=["POST"])
def firebase_login():

    id_token = request.json.get("idToken")

    decoded = auth.verify_id_token(id_token)

    uid = decoded["uid"]
    email = decoded.get("email")
    phone = decoded.get("phone_number")
    name = decoded.get("name") or "User"
    photo = decoded.get("picture")

    doc=firebase_services.get_user_by_uid(uid)

    # NEW USER
    if not doc:
        firebase_services.add_user(uid,email,name,photo)

        session["user"]={
            "uid": uid,
            "name": name,
            "photo_url": photo
        }

        return {"status": "new"}

    # EXISTING USER
    role = doc.get("role")

    session["user"]={
            "uid": uid,
            "name": name,
            "photo_url": photo
        }


    return {"status": "existing", "role": role}

@app.route("/api/update-profile", methods=["POST"])
def update_profile():

    if "user" not in session:
        return {"success": False}, 401

    uid = session["user"]["uid"]
    data = request.get_json()
    firebase_services.update_user_profile(uid, data)

    return {"success": True}

@app.route("/profile/<slug>")
def worker_profile(slug):
    return render_template("worker_profile.html", slug=slug)

# ======================
# Role Setup (First Time)
# ======================
@app.route("/select-role", methods=["GET", "POST"])
def select_role():

    # Must be logged in
    if not session["user"]:
        return redirect("/")

    uid = session["user"]["uid"]

    # ------------------
    # GET → Show page
    # ------------------
    if request.method == "GET":

        user_dic = firebase_services.get_user_by_uid(uid)

        # If role already chosen, skip this page
        if user_dic and user_dic.get("role"):
            role = user_dic["role"]

            if role == "worker":
                return redirect("/worker/dashboard")
            else:
                return redirect("/customer/dashboard")

        # Otherwise show role selection
        return render_template("choose_role.html")

    # ------------------
    # POST → Save role
    # ------------------
    role = request.json.get("role")

    if role not in ["customer", "worker"]:
        return {"success": False}, 400

    # Update users collection
    firebase_services.update_role(uid, role)
    # If worker, create worker doc
    if role == "worker":
        firebase_services.create_worker_profile(uid, {
            "name": session["user"]["name"],
            "phone": None,
            "email": None,
            "address": None,
            "skills": []
        })

    session["role"] = role

    return {"success": True}


# ======================
# Dashboards
# ======================

@app.route("/worker/dashboard")
def worker_dashboard():
    
    return render_template("worker_dashboard.html")

@app.route("/customer/dashboard")
def customer_dashboard():
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
