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

def update_role(uid, role):
    db.collection("users").document(uid).update({
        "role": role,
        "updatedAt": firestore.SERVER_TIMESTAMP
    })
def update_user_profile(uid,data):
    
    db.collection("users").document(uid).update({
        "name": data["name"],
        "phone": data["phone"],
        "email": data["email"],
        "address": data["address"],
        "photo_url": data["photo_url"],
        "updatedAt": firestore.SERVER_TIMESTAMP
    })
def create_worker_profile(uid,data):
    db.collection("workers").document(uid).set({
        "name": data["name"],
        "phone": data["phone"],
        "email": data["email"],
        "address": data["address"],
        "skills": data["skills"],
        "updatedAt": firestore.SERVER_TIMESTAMP
    })


# ======================
# ongoing jobs
# ======================
def get_ongoing_jobs_for_user(uid, role):
    if role == "customer":
        jobs_ref = db.collection("jobs").where("customerId", "==", uid).where("status", "in", ["accepted", "in_progress"])
        jobs=[]
        for doc in jobs_ref.stream():
            wid=doc.to_dict().get("workerId")
            workern=db.collection("workers").document(wid).get().to_dict().get("name")
            job = doc.to_dict()
            job["workerName"] = workern
            jobs.append(job)
    else:
        jobs_ref = db.collection("jobs").where("workerId", "==", uid).where("status", "in", ["accepted", "in_progress"])

    return jobs

# ======================
# previous jobs
# ======================
def get_previous_jobs_for_user(uid, role):
    if role == "customer":
        jobs_ref = db.collection("jobs").where("customerId", "==", uid).where("status", "==", "completed")
        jobs=[]
        for doc in jobs_ref.stream():
            wid=doc.to_dict().get("workerId")
            workern=db.collection("workers").document(wid).get().to_dict().get("name")
            job = doc.to_dict()
            job["workerName"] = workern
            jobs.append(job)
    else:
        jobs_ref = db.collection("jobs").where("workerId", "==", uid).where("status", "==", "completed")

    return jobs  

def save_worker_for_customer(customer_uid, worker_uid):
    customer_ref = db.collection("users").document(customer_uid)
    customer_ref.update({
        "saved_workers": firestore.ArrayUnion([worker_uid]),
        "updatedAt": firestore.SERVER_TIMESTAMP
    })
def remove_saved_worker_for_customer(customer_uid, worker_uid):
    customer_ref = db.collection("users").document(customer_uid)
    customer_ref.update({
        "saved_workers": firestore.ArrayRemove([worker_uid]),
        "updatedAt": firestore.SERVER_TIMESTAMP
    })
def get_saved_workers_for_customer(customer_uid):
    customer_doc = db.collection("users").document(customer_uid).get()
    if customer_doc.exists:
        saved_ids = customer_doc.to_dict().get("saved_workers", [])
        saved_workers = []
        for wid in saved_ids:
            w = db.collection("workers").document(wid).get()
            if w.exists:
                saved_workers.append(w.to_dict())
        return saved_workers
    return []
def get_chats_for_user(uid):
    chats = []
    chat_Ref = db.collection("conversations").where("customerId", "==", uid).limit(5)
    for doc in chat_Ref.stream():
        chats.append(doc.to_dict())
    return chats
def get_chats_for_worker(uid):
    chats = []
    chat_Ref = db.collection("conversations").where("workerId", "==", uid).limit(5)
    for doc in chat_Ref.stream():
        chats.append(doc.to_dict())
    return chats                     
def update_worker_profile(uid,data):
    db.collection("workers").document(uid).set({

        "uid": uid,
        "name": data["name"],
        "trade": data["trade"],
        "experience": data["experience"],
        "city": data["city"],
        "skills": data["skills"],
        "radius": data["radius"],
        "bio": data["bio"],
        "price": data["price"],
        "availability": data["availability"],
        "emergency": data["emergency"],

        "avatar_url": data["avatar_url"],

        "rating": 0,
        "totalJobs": 0,
        "verified": False,

        "createdAt": firestore.SERVER_TIMESTAMP

    }, merge=True)
def update_worker_At_user(uid,name,photo_url):
    db.collection("users").document(uid).update({
        "name": name,
        "photo_url": photo_url,
        "updatedAt": firestore.SERVER_TIMESTAMP
    })