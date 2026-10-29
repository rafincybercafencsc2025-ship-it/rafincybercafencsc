import os
import sqlite3
import secrets
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deploy-" + secrets.token_hex(16))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "retailer.db"))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS retailers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        retailer_id TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("retailer_id"):
            flash("প্রথমে লগইন করুন।", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admin login প্রয়োজন।", "warning")
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        if not all([name, email, phone, password]):
            flash("সব ঘর পূরণ করুন।", "danger")
            return render_template("register.html")
        if len(password) < 8:
            flash("পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।", "danger")
            return render_template("register.html")
        try:
            db().execute(
                "INSERT INTO retailers (name,email,phone,password_hash) VALUES (?,?,?,?)",
                (name, email, phone, generate_password_hash(password))
            )
            db().commit()
        except sqlite3.IntegrityError:
            flash("এই ইমেল দিয়ে আগে রেজিস্ট্রেশন হয়েছে।", "danger")
            return render_template("register.html")
        flash("রেজিস্ট্রেশন সফল। Admin অনুমোদন দিলে Retailer ID চালু হবে।", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db().execute("SELECT * FROM retailers WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            if user["status"] != "Approved":
                flash("আপনার অ্যাকাউন্ট এখনও Admin অনুমোদন করেননি।", "warning")
                return render_template("login.html")
            session.clear()
            session["retailer_id"] = user["retailer_id"]
            session["retailer_name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("ইমেল অথবা পাসওয়ার্ড সঠিক নয়।", "danger")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user = db().execute("SELECT * FROM retailers WHERE retailer_id=?", (session["retailer_id"],)).fetchone()
    return render_template("dashboard.html", user=user)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USERNAME and request.form.get("password") == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Admin username অথবা password ভুল।", "danger")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    users = db().execute("SELECT * FROM retailers ORDER BY created_at DESC").fetchall()
    return render_template("admin_dashboard.html", users=users)

@app.post("/admin/approve/<int:user_id>")
@admin_required
def approve(user_id):
    user = db().execute("SELECT * FROM retailers WHERE id=?", (user_id,)).fetchone()
    if user:
        retailer_id = user["retailer_id"] or f"RAFIN{user_id:05d}"
        db().execute("UPDATE retailers SET status='Approved', retailer_id=? WHERE id=?", (retailer_id, user_id))
        db().commit()
        flash(f"{user['name']} অনুমোদিত। Retailer ID: {retailer_id}", "success")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/reject/<int:user_id>")
@admin_required
def reject(user_id):
    db().execute("UPDATE retailers SET status='Rejected', retailer_id=NULL WHERE id=?", (user_id,))
    db().commit()
    flash("রেজিস্ট্রেশন বাতিল করা হয়েছে।", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    flash("আপনি লগআউট করেছেন।", "info")
    return redirect(url_for("index"))

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
