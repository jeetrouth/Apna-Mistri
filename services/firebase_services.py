import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os,json
from flask import jsonify
from datetime import datetime, timedelta
import pytz
firebase_creds = os.environ.get("FIREBASE_CONFIG")

if firebase_creds:
    cred_dict = json.loads(firebase_creds)
    cred = credentials.Certificate(cred_dict)
else:
    # fallback for local dev
    raise Exception("FIREBASE_SERVICE_ACCOUNT environment variable not set")

# ======================
# Firebase Init
# ======================

# Avoid 'app already exists' error if this file is imported more than once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


# --- User Functions ---
def add_user(uid,email,name,photo_url):
    user_ref = db.collection("users").document(uid)
    user_ref.set({
        "uid": uid,
        "name": name,
        "email": email,
        "createdAt": firestore.SERVER_TIMESTAMP,
        "hydration_enabled": False,
        "photo_url":photo_url,
        "role":None,
        "phone":None
    })

def add_user_phone(uid, phone, name, photo_url):
    db.collection("users").document(uid).set({
        "uid": uid,
        "phone": phone,
        "name": name,
        "photo_url": photo_url,
        "role": None,
        "createdAt": firestore.SERVER_TIMESTAMP
    })
def get_user_by_uid(uid):
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None

def update_user_profile(uid,data):
    
    db.collection("users").document(uid).update({
        "name": data["name"],
        "phone": data["phone"],
        "email": data["email"],
        "address": data["address"],
        "updatedAt": firestore.SERVER_TIMESTAMP
    })
