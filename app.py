import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# ------------------------
# Environment Setup
# ------------------------
load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("⚠️ DATABASE_URL not found. Using local SQLite database.")
    DATABASE_URL = "sqlite:///tiffintrack.db"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "tiffintrack-secret-key-2026")

db = SQLAlchemy(app)

# ------------------------
# Models
# ------------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    addr1 = db.Column(db.String(255), nullable=False)
    addr2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Plan(db.Model):
    __tablename__ = "plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    daily_rate = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)


class CustomerPlan(db.Model):
    __tablename__ = "customer_plans"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class PausedDate(db.Model):
    __tablename__ = "paused_dates"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pause_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


# ------------------------
# Seed Default Plans
# ------------------------

def seed_plans():
    if Plan.query.count() == 0:
        plans = [
            Plan(name="Veg Thali", daily_rate=120, description="Standard veg meal"),
            Plan(name="Diet Meal", daily_rate=150, description="Low calorie diet meal"),
            Plan(name="Non-Veg Thali", daily_rate=180, description="Chicken based meal"),
        ]
        db.session.bulk_save_objects(plans)
        db.session.commit()
        print("✅ Default plans seeded")


# ------------------------
# Initialize Database
# ------------------------

with app.app_context():
    db.create_all()
    seed_plans()


# ------------------------
# Routes
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")

        # Static Admin
        if email == "admin@tiffintrack.com" and password == "admin123":
            session["user_id"] = 0
            session["user_name"] = "Admin"
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.fullname
            session["is_admin"] = user.is_admin
            return redirect(url_for("customer_dashboard"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ---------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").lower().strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        addr1 = request.form.get("addr1", "").strip()
        addr2 = request.form.get("addr2", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Email already registered")

        user = User(
            fullname=fullname,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            addr1=addr1,
            addr2=addr2,
            city=city,
            state=state,
            pincode=pincode,
        )

        db.session.add(user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---------- Admin ----------
@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")


# ---------- Customer ----------
@app.route("/dashboard")
def customer_dashboard():
    if "user_id" not in session or session.get("is_admin"):
        return redirect(url_for("login"))
    return render_template("customer_dashboard.html")


# ---------- Pause ----------
@app.route("/pause")
def pause_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    paused = PausedDate.query.filter_by(customer_id=session["user_id"]).all()
    paused_dates = [p.pause_date.strftime("%Y-%m-%d") for p in paused]

    return render_template("pause_calendar.html", paused_dates=paused_dates)


@app.route("/pause/save", methods=["POST"])
def save_pause():
    if "user_id" not in session:
        return redirect(url_for("login"))

    selected_date = request.form.get("pause_date")
    pause_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    if pause_date < date.today():
        flash("Cannot pause past dates", "error")
        return redirect(url_for("pause_page"))

    exists = PausedDate.query.filter_by(
        customer_id=session["user_id"],
        pause_date=pause_date
    ).first()

    if exists:
        flash("This date is already paused", "error")
        return redirect(url_for("pause_page"))

    db.session.add(
        PausedDate(
            customer_id=session["user_id"],
            pause_date=pause_date
        )
    )
    db.session.commit()
    flash("Tiffin paused successfully", "success")

    return redirect(url_for("pause_page"))


# ---------- Plans ----------
@app.route("/plans")
def choose_plans():
    if "user_id" not in session:
        return redirect(url_for("login"))

    plans = Plan.query.filter_by(is_active=True).all()
    return render_template("choose_plans.html", plans=plans, date=date)


@app.route("/plans/save", methods=["POST"])
def save_plans():
    if "user_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["user_id"]

    # Remove old plans
    CustomerPlan.query.filter_by(customer_id=customer_id).delete()
    db.session.commit()

    for key in request.form:
        if key.startswith("plan_"):
            plan_id = int(key.split("_")[1])
            start_date_str = request.form.get(f"start_{plan_id}")
            end_date_str = request.form.get(f"end_{plan_id}")

            if not start_date_str or not end_date_str:
                continue

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if end_date < start_date:
                continue

            db.session.add(
                CustomerPlan(
                    customer_id=customer_id,
                    plan_id=plan_id,
                    start_date=start_date,
                    end_date=end_date,
                )
            )

    db.session.commit()
    flash("Plans saved successfully", "success")
    return redirect(url_for("customer_dashboard"))


# ---------- Billing ----------
@app.route("/billing")
def billing_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["user_id"]

    rows = (
        db.session.query(CustomerPlan, Plan)
        .join(Plan, CustomerPlan.plan_id == Plan.id)
        .filter(CustomerPlan.customer_id == customer_id)
        .all()
    )

    billing_rows = []
    grand_total = 0

    for cp, plan in rows:
        paused_count = PausedDate.query.filter(
            PausedDate.customer_id == customer_id,
            PausedDate.pause_date >= cp.start_date,
            PausedDate.pause_date <= cp.end_date,
        ).count()

        total_days = (cp.end_date - cp.start_date).days + 1
        active_days = max(total_days - paused_count, 0)
        amount = active_days * plan.daily_rate

        grand_total += amount

        billing_rows.append({
            "plan": plan.name,
            "rate": plan.daily_rate,
            "total_days": total_days,
            "paused_days": paused_count,
            "billable_days": active_days,
            "amount": amount,
        })

    return render_template(
        "billing.html",
        billing_rows=billing_rows,
        grand_total=grand_total
    )

@app.route("/terms")
def terms():
    return render_template("terms.html")

# ------------------------
# Run App
# ------------------------

if __name__ == "__main__":
    app.run(debug=True)
