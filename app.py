from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from services import firebase_services, imagekit_services
from firebase_admin import auth

from PIL import Image
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
            "photo_url": photo,
            "role": role
        }


    return {"status": "existing", "role": role}

@app.route("/user/setup", methods=["GET", "POST"])
def user_setup():

    if not session["user"]:
        return redirect("/")

    uid = session["user"]["uid"]

    if request.method == "GET":
        return render_template("usersetup.html")

    # ---------- POST ----------

    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    address = request.form.get("address")
    city = request.form.get("city")
    pincode = request.form.get("pincode")
    addr={
        "fulladdr": address,
        "city": city,
        "pincode": pincode
    }
    photo = request.files.get("photo")

    photo_url = None

    if photo:
        from PIL import Image
        from services.imagekit_services import upload_user_profile

        img = Image.open(photo)
        result = upload_user_profile(uid, img)
        photo_url = result["url"]
    data={
        "name": name,
        "phone": phone,
        "email": email,
        "address": addr,
        "photo_url": photo_url}
    # Update users collection (customer profile lives here)
    firebase_services.update_user_profile(uid,data)

    return {"success": True}



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
@app.route("/worker/onboarding", methods=["GET", "POST"])
def worker_onboarding():

    if not  session["user"]:
        return redirect("/")

    uid = session["user"]["uid"]

    if request.method == "GET":
        return render_template("worker_onboarding.html")

    # -------- POST --------

    name = request.form.get("name")
    trade = request.form.get("trade")
    trade_other = request.form.get("trade_other")

    if trade == "Other" and trade_other:
        trade = trade_other

    experience = request.form.get("experience")
    experience_other = request.form.get("experience_other")

    if experience == "Other" and experience_other:
        experience = experience_other

    city = request.form.get("city")
    skills = request.form.getlist("skills")
    radius = request.form.get("radius")
    bio = request.form.get("bio")
    price = request.form.get("price")
    availability = request.form.get("availability")
    emergency = request.form.get("emergency")

    photo = request.files.get("photo")

    avatar_url = None

    if photo:
        img = Image.open(photo)
        result = imagekit_services.upload_worker_avatar(uid, img)
        avatar_url = result["url"] if result else None

    # Update USERS (identity)
    firebase_services.update_worker_At_user(uid, name, avatar_url)

    # Create / update WORKERS (professional profile)
    firebase_services.update_worker_profile(uid, {
        "name": name,
        "trade": trade,
        "experience": experience,
        "city": city,
        "skills": skills,
        "radius": radius,
        "bio": bio,
        "price": price,
        "availability": availability,
        "emergency": emergency,
        "avatar_url": avatar_url
    })

    return redirect("/worker/dashboard")

@app.route("/dashboard")
def dashboard():
    if not session["user"]:
        return redirect("/")

    if session["user"]["role"] == "worker":
        return redirect("/worker/dashboard")
    else:
        return redirect("/customer/dashboard")

@app.route("/worker/dashboard")
def worker_dashboard():
    
    return render_template("worker_dashboard.html")

@app.route("/customer/dashboard")
def customer_dashboard():
    return render_template("customer_dashboard.html",user=session["user"])

@app.route("/api/customer/dashboard",methods=["GET"])
def customer_dashboard_data():

    if not session["user"]:
        return {"error": "unauthorized"}, 401

    uid = session["user"]["uid"]

    # --- Ongoing Jobs ---
    ongoing = firebase_services.get_ongoing_jobs_for_user(uid, "customer")
    # --- Previous Jobs ---
    previous = firebase_services.get_previous_jobs_for_user(uid, "customer")
    # --- Saved Workers ---
    saved_workers = firebase_services.get_saved_workers_for_customer(uid)

    # --- Chats ---
    chats = firebase_services.get_chats_for_user(uid)

    return {
        "ongoing_jobs": ongoing,
        "previous_jobs": previous,
        "saved_workers": saved_workers,
        "recent_chats": chats
    }

@app.route("/chat/start", methods=["POST"])
def start_chat():

    if not session["user"]:
        return {"error": "unauthorized"}, 401

    uid = session["user"]["uid"]
    worker_id = request.json.get("workerId")

    # Check existing conversation
    existing = firebase_services.get_existing_conversation(uid, worker_id)
    if existing:
        return existing
    # Create new conversation
    convo = firebase_services.create_new_conversation(uid, worker_id)
    if convo:
        return convo



@app.route("/api/conversations")
def get_conversations():

    if  not session["user"]:
        return [], 401

    uid = session["user"]["uid"]
    chats = firebase_services.get_conversations_for_user(uid)
    return chats


@app.route("/api/messages/<cid>")
def get_messages(cid):

    if  not  session["user"]:
        return [], 401

    msgs= firebase_services.get_messages_from_cid(cid)
    return msgs

@app.route("/api/send/<cid>", methods=["POST"])
def send_message(cid):

    if not session["user"]:
        return {"error": "unauthorized"}, 401

    uid = session["user"]["uid"]
    text = request.json.get("text")

    if not text:
        return {"error": "empty"}, 400

    
    try:
        firebase_services.send_message(cid, uid, text)
    except Exception as e:
        print("Error sending message:", e)
        return {"error": "Failed to send message"}, 500

    

    return {"success": True}


@app.route("/inbox")
def inbox():

    if not session["user"]:
        return redirect("/")

    return render_template("inbox.html", user=session["user"])


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")

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
