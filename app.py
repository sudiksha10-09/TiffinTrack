import os
import json
import stripe
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, time, timedelta
from calendar import monthrange
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from PIL import Image
import stripe

# ------------------------
# Environment Setup
# ------------------------
load_dotenv()

app = Flask(__name__)

# Database Configuration for Neon PostgreSQL with Enhanced Connection Handling
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Default to Neon PostgreSQL
    DATABASE_URL = "postgresql://neondb_owner:npg_nsMXcjJ1pB9t@ep-red-paper-ah0u6oe0-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Enhanced connection handling for Neon with retry logic
def get_database_url():
    """Get working database URL with fallback options"""
    import psycopg2
    import time
    
    # Primary Neon URL (with pooler)
    primary_url = DATABASE_URL
    
    # Alternative Neon URLs to try
    fallback_urls = []
    
    if "pooler" in DATABASE_URL:
        # Direct connection without pooler
        direct_url = DATABASE_URL.replace("-pooler", "")
        fallback_urls.append(direct_url)
        
        # Try with different SSL modes
        fallback_urls.append(DATABASE_URL.replace("?sslmode=require", "?sslmode=prefer"))
        fallback_urls.append(direct_url.replace("?sslmode=require", "?sslmode=prefer"))
        fallback_urls.append(DATABASE_URL.replace("?sslmode=require", "?sslmode=disable"))
    
    # Try each URL with retry logic
    urls_to_try = [primary_url] + fallback_urls
    
    for i, url in enumerate(urls_to_try):
        for attempt in range(2):  # Reduced to 2 attempts per URL for faster fallback
            try:
                print(f"🔄 Attempting connection {i+1}/{len(urls_to_try)}, try {attempt+1}/2...")
                # Set a shorter timeout for faster fallback
                test_conn = psycopg2.connect(url, connect_timeout=5)
                test_conn.close()
                
                connection_type = "pooled" if "pooler" in url else "direct"
                ssl_mode = "require" if "sslmode=require" in url else "prefer" if "sslmode=prefer" in url else "disable"
                print(f"✅ Connected to Neon PostgreSQL ({connection_type}, SSL: {ssl_mode})")
                return url
                
            except Exception as e:
                print(f"⚠️ Connection attempt failed: {str(e)[:100]}...")
                if attempt < 1:  # Don't sleep on last attempt
                    time.sleep(1)  # Reduced sleep time
                continue
    
    # If all Neon connections fail, fall back to SQLite
    print("❌ All Neon PostgreSQL connection attempts failed")
    print("🔄 Falling back to SQLite for development...")
    
    sqlite_url = "sqlite:///tiffintrack.db"
    print(f"✅ Using SQLite database: {sqlite_url}")
    return sqlite_url

# Get the working database URL
working_db_url = get_database_url()
app.config["SQLALCHEMY_DATABASE_URI"] = working_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "tiffintrack-secret-key-2026")

# Enhanced SQLAlchemy configuration for Neon PostgreSQL
if "sqlite" in working_db_url:
    # SQLite configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_timeout": 30,
        "pool_recycle": 300,
        "pool_pre_ping": True
    }
else:
    # PostgreSQL configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 5,
        "pool_timeout": 30,
        "pool_recycle": 300,  # Recycle connections every 5 minutes
        "pool_pre_ping": True,  # Verify connections before use
        "max_overflow": 10,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": "TiffinTrack"
            # Removed statement_timeout as it's not supported by Neon pooled connections
        }
    }

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

# Stripe Configuration
stripe.api_key = STRIPE_SECRET_KEY
app.config["STRIPE_PUBLISHABLE_KEY"] = STRIPE_PUBLISHABLE_KEY

# ------------------------
# Email Configuration
# ------------------------

SMTP_HOST = os.getenv("SMTP_SERVER")  # Changed from SMTP_HOST to match .env.example
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
MAIL_DEFAULT_SENDER = os.getenv("SENDER_EMAIL", "no-reply@tiffintrack.com")  # Changed from MAIL_DEFAULT_SENDER to SENDER_EMAIL


def is_email_configured() -> bool:
    """Return True if all required SMTP settings are present."""
    return all([SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, MAIL_DEFAULT_SENDER])


def send_email(to_email: str, subject: str, html_body: str, text_body: str | None = None) -> tuple[bool, str | None]:
    """
    Send an email using SMTP settings from environment variables.
    Returns (success, error_message).
    """
    if not is_email_configured():
        return False, "Email service is not configured. Please set SMTP_* environment variables."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = MAIL_DEFAULT_SENDER
        msg["To"] = to_email

        if not text_body:
            text_body = html_body

        part_text = MIMEText(text_body, "plain")
        part_html = MIMEText(html_body, "html")
        msg.attach(part_text)
        msg.attach(part_html)

        if SMTP_USE_TLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(MAIL_DEFAULT_SENDER, [to_email], msg.as_string())
        else:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context()) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(MAIL_DEFAULT_SENDER, [to_email], msg.as_string())

        return True, None
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False, str(e)

# File Upload Configuration
UPLOAD_FOLDER = 'static/uploads/dishes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database retry decorator for handling connection drops
from functools import wraps
import time as time_module
from sqlalchemy.exc import OperationalError, DisconnectionError

def db_retry(max_retries=3, delay=1):
    """Decorator to retry database operations on connection failures"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError) as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Check if it's a connection-related error
                    if any(keyword in error_msg for keyword in [
                        'connection abort', 'ssl syscall', 'server closed', 
                        'connection reset', 'broken pipe', 'timeout'
                    ]):
                        print(f"🔄 Database connection error (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}...")
                        
                        if attempt < max_retries - 1:
                            # Exponential backoff
                            sleep_time = delay * (2 ** attempt)
                            print(f"⏳ Retrying in {sleep_time} seconds...")
                            time_module.sleep(sleep_time)
                            
                            # Try to refresh the connection
                            try:
                                db.engine.dispose()
                                print("🔄 Database connection pool refreshed")
                            except:
                                pass
                            continue
                    else:
                        # Not a connection error, re-raise immediately
                        raise e
                except Exception as e:
                    # Non-connection error, re-raise immediately
                    raise e
            
            # All retries failed
            print(f"❌ All database retry attempts failed")
            raise last_exception
        return wrapper
    return decorator

# Database connection verification with retry
@db_retry(max_retries=3, delay=2)
def verify_database_connection():
    """Verify database connection and setup with retry logic"""
    try:
        with app.app_context():
            db_uri = app.config["SQLALCHEMY_DATABASE_URI"]

            # Create tables automatically for SQLite and for empty PostgreSQL schemas
            if "sqlite" in db_uri or "postgresql" in db_uri:
                try:
                    # Try a lightweight query against the users table to see if schema exists
                    db.session.execute(db.text("SELECT 1 FROM users LIMIT 1"))
                    db.session.commit()
                    print("✅ Existing database schema detected")
                except Exception as schema_error:
                    # If the users table (or others) are missing, create all tables
                    print(f"ℹ️ Database schema missing or incomplete, creating tables… ({schema_error})")
                    db.create_all()

                    # Seed initial data if no users exist
                    if User.query.count() == 0:
                        print("🌱 Seeding initial data...")
                        seed_initial_data()

            # Test connection with a simple query
            connection = db.engine.connect()
            result = connection.execute(db.text("SELECT 1"))
            result.fetchone()
            connection.close()
            
            # Check if we have data
            user_count = User.query.count()
            db_type = "SQLite" if "sqlite" in db_uri else "PostgreSQL"
            print(f"✅ {db_type} database ready with {user_count} users")
            
        return True
    except Exception as e:
        print(f"❌ Database connection verification failed: {e}")
        raise

if "mysql" in working_db_url:
    print(f"🔗 Connected to MySQL database")
elif "postgresql" in working_db_url:
    print(f"🔗 Connected to Neon PostgreSQL database")
else:
    print(f"🔗 Using SQLite database for development")

# Template filters
@app.template_filter('strptime')
def strptime_filter(date_string, format='%Y-%m-%d'):
    """Parse date string to datetime object"""
    return datetime.strptime(date_string, format).date()

@app.template_filter('strftime')
def strftime_filter(date_obj, format='%Y-%m-%d'):
    """Format date object to string"""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime(format) if date_obj else ''

@app.template_filter('from_json')
def from_json_filter(json_string):
    """Parse JSON string to Python object"""
    try:
        return json.loads(json_string) if json_string else []
    except:
        return []

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(800, 600)):
    """Resize image to max dimensions while maintaining aspect ratio"""
    with Image.open(image_path) as img:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(image_path, optimize=True, quality=85)

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
    area = db.Column(db.String(100), nullable=False)  # Navi Mumbai areas
    city = db.Column(db.String(100), nullable=False, default="Navi Mumbai")
    state = db.Column(db.String(100), nullable=False, default="Maharashtra")
    pincode = db.Column(db.String(10), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Plan(db.Model):
    __tablename__ = "plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    daily_rate = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)  # Changed from String(255) to Text for longer descriptions
    items = db.Column(db.Text)  # JSON string of menu items
    image_filename = db.Column(db.String(255))  # Image file name
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class CustomerPlan(db.Model):
    __tablename__ = "customer_plans"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class PausedDate(db.Model):
    __tablename__ = "paused_dates"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pause_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Bill(db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    paused_days = db.Column(db.Integer, nullable=False)
    billable_days = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Menu(db.Model):
    __tablename__ = "menus"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(255), unique=True, nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Amount in paise (₹1 = 100 paise)
    currency = db.Column(db.String(3), default="inr", nullable=False)
    status = db.Column(db.String(50), nullable=False)  # succeeded, pending, failed
    payment_method = db.Column(db.String(50))  # card, upi, netbanking, etc.
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class PaymentLog(db.Model):
    __tablename__ = "payment_logs"

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50))
    stripe_payment_intent_id = db.Column(db.String(255), unique=True, nullable=False)
    billing_period = db.Column(db.String(20))  # "MM/YYYY" format
    status = db.Column(db.String(50), default="completed")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # Relationships for easy access
    payment = db.relationship("Payment", backref="logs")
    bill = db.relationship("Bill", backref="payment_logs")
    customer = db.relationship("User", backref="payment_logs")


# ------------------------
# Navi Mumbai Areas Configuration
# ------------------------

NAVI_MUMBAI_AREAS = [
    "Vashi", "Nerul", "Belapur", "Kharghar", "Panvel", "Kamothe", 
    "Ghansoli", "Kopar Khairane", "Airoli", "Sanpada", "Juinagar",
    "Seawoods", "Darave", "Digha", "Karave", "Ulwe"
]

# ------------------------
# Seed Functions (for initial data only)
# ------------------------

def seed_initial_data():
    """Seed initial data - only run once after migration"""
    # Create default plans if they don't exist
    if Plan.query.count() == 0:
        plans = [
            Plan(
                name="Veg Thali", 
                daily_rate=120, 
                description="Complete vegetarian meal with rice, dal, sabzi, roti, and salad",
                items='["Basmati Rice", "Dal Tadka", "Mixed Vegetable Curry", "2 Rotis", "Fresh Salad", "Pickle"]'
            ),
            Plan(
                name="Diet Special", 
                daily_rate=150, 
                description="Low calorie, high protein meal for fitness enthusiasts",
                items='["Brown Rice", "Moong Dal", "Steamed Vegetables", "Multigrain Roti", "Sprouts Salad"]'
            ),
            Plan(
                name="Non-Veg Thali", 
                daily_rate=180, 
                description="Delicious non-vegetarian meal with chicken curry",
                items='["Basmati Rice", "Dal", "Chicken Curry", "2 Rotis", "Raita", "Pickle"]'
            ),
        ]
        for plan in plans:
            db.session.add(plan)
        db.session.commit()
        print("✅ Default plans seeded")

    # Create default admin user if doesn't exist
    admin = User.query.filter_by(email="admin@tiffintrack.com").first()
    if not admin:
        admin = User(
            fullname="TiffinTrack Admin",
            email="admin@tiffintrack.com",
            phone="9000000000",
            password=generate_password_hash("admin123"),
            addr1="Admin Office, Plot 123",
            addr2="Sector 15",
            area="Vashi",
            city="Navi Mumbai",
            state="Maharashtra",
            pincode="400703",
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin user created")
    
    # Create sample customers if they don't exist
    if User.query.filter_by(is_admin=False).count() == 0:
        sample_customers = [
            {
                "fullname": "Rahul Sharma",
                "email": "rahul.sharma@email.com",
                "phone": "9876543210",
                "password": generate_password_hash("password123"),
                "addr1": "Flat 301, Sai Residency",
                "addr2": "Sector 7",
                "area": "Vashi",
                "pincode": "400703"
            },
            {
                "fullname": "Priya Patel",
                "email": "priya.patel@email.com", 
                "phone": "9876543211",
                "password": generate_password_hash("password123"),
                "addr1": "B-204, Palm Beach Residency",
                "addr2": "Sector 19D",
                "area": "Nerul",
                "pincode": "400706"
            },
            {
                "fullname": "Amit Kumar",
                "email": "amit.kumar@email.com",
                "phone": "9876543212", 
                "password": generate_password_hash("password123"),
                "addr1": "Tower 3, Flat 1205, Seawoods Grand Central",
                "addr2": "Plot 2A",
                "area": "Seawoods",
                "pincode": "400706"
            }
        ]
        
        for customer_data in sample_customers:
            customer = User(
                fullname=customer_data["fullname"],
                email=customer_data["email"],
                phone=customer_data["phone"],
                password=customer_data["password"],
                addr1=customer_data["addr1"],
                addr2=customer_data["addr2"],
                area=customer_data["area"],
                city="Navi Mumbai",
                state="Maharashtra",
                pincode=customer_data["pincode"],
                is_admin=False
            )
            db.session.add(customer)
        
        db.session.commit()
        print("✅ Sample customers created")


# ------------------------
# Routes
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
@db_retry(max_retries=2, delay=1)
def health_check():
    """Health check endpoint to verify database connectivity"""
    try:
        # Test database connection
        connection = db.engine.connect()
        result = connection.execute(db.text("SELECT 1 as health_check"))
        result.fetchone()
        connection.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)[:200],
            "timestamp": datetime.now().isoformat()
        }), 503


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.fullname
            session["is_admin"] = user.is_admin
            
            if user.is_admin:
                flash(f"Welcome back, {user.fullname}!", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                flash(f"Welcome back, {user.fullname}!", "success")
                return redirect(url_for("customer_dashboard"))

        flash("Invalid email or password", "error")
        return render_template("login.html")

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

        # Restrict registration to supported Navi Mumbai areas only
        area = request.form.get("area", "").strip()
        if area not in NAVI_MUMBAI_AREAS:
            return render_template("register.html", error="Please select a valid delivery area in Navi Mumbai")

        user = User(
            fullname=fullname,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            addr1=addr1,
            addr2=addr2,
            area=area or "Vashi",
            city="Navi Mumbai",
            state="Maharashtra",
            pincode=pincode,
        )

        db.session.add(user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """View and update the logged in user's profile details."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])
    
    # Check if user has active plans
    has_active_plans = CustomerPlan.query.filter_by(
        customer_id=user.id,
        is_active=True
    ).filter(CustomerPlan.end_date >= date.today()).count() > 0

    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").lower().strip()
        phone = request.form.get("phone", "").strip()
        addr1 = request.form.get("addr1", "").strip()
        addr2 = request.form.get("addr2", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        area = request.form.get("area", "").strip()

        if not fullname or not email or not phone or not addr1 or not city or not state or not pincode or not area:
            flash("Please fill in all required fields.", "error")
            return render_template("profile.html", user=user, is_admin=user.is_admin, areas=NAVI_MUMBAI_AREAS, has_active_plans=has_active_plans)

        if area not in NAVI_MUMBAI_AREAS:
            flash("Please select a valid delivery area in Navi Mumbai.", "error")
            return render_template("profile.html", user=user, is_admin=user.is_admin, areas=NAVI_MUMBAI_AREAS, has_active_plans=has_active_plans)

        # Check if address fields are being changed and user has active plans
        address_changed = (
            addr1 != user.addr1 or 
            addr2 != user.addr2 or 
            area != user.area or 
            city != user.city or 
            state != user.state or 
            pincode != user.pincode
        )
        
        if address_changed and has_active_plans:
            flash("Cannot change address while you have active meal plans. Please wait until your current plans end or contact support.", "error")
            return render_template("profile.html", user=user, is_admin=user.is_admin, areas=NAVI_MUMBAI_AREAS, has_active_plans=has_active_plans)

        # Ensure email uniqueness if changing
        if email != user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash("That email address is already in use.", "error")
                return render_template("profile.html", user=user, is_admin=user.is_admin, areas=NAVI_MUMBAI_AREAS, has_active_plans=has_active_plans)

        user.fullname = fullname
        user.email = email
        user.phone = phone
        user.addr1 = addr1
        user.addr2 = addr2
        user.city = city
        user.state = state
        user.pincode = pincode
        user.area = area

        db.session.commit()

        # Keep session display name up to date
        session["user_name"] = user.fullname

        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user, is_admin=user.is_admin, areas=NAVI_MUMBAI_AREAS, has_active_plans=has_active_plans)


@app.route("/change-password", methods=["POST"])
def change_password():
    """Change user password"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        current_password = data.get("current_password", "").strip()
        new_password = data.get("new_password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()
        
        if not current_password or not new_password or not confirm_password:
            return jsonify({"error": "All fields are required"}), 400
        
        if new_password != confirm_password:
            return jsonify({"error": "New passwords do not match"}), 400
        
        if len(new_password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        user = User.query.get(session["user_id"])
        
        # Verify current password
        if not check_password_hash(user.password, current_password):
            return jsonify({"error": "Current password is incorrect"}), 400
        
        # Update password
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        })
        
    except Exception as e:
        print(f"Error changing password: {e}")
        return jsonify({"error": "Failed to change password"}), 500


# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---------- Admin Dashboard ----------
@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    # Get real statistics
    total_customers = User.query.filter_by(is_admin=False).count()
    active_plans = CustomerPlan.query.filter_by(is_active=True).count()
    today_paused = PausedDate.query.filter_by(pause_date=date.today()).count()
    pending_bills = Bill.query.filter_by(is_paid=False).count()
    
    # Calculate today's meals
    today_meals = active_plans - today_paused
    
    # Get current date formatted
    current_date = date.today().strftime('%B %d, %Y')
    
    stats = {
        'total_customers': total_customers,
        'today_meals': today_meals,
        'today_paused': today_paused,
        'pending_bills': pending_bills
    }
    
    return render_template(
        "admin_dashboard.html",
        stats=stats,
        current_date=current_date,
        email_configured=is_email_configured(),
    )


@app.route("/admin/test-email")
def admin_test_email():
    """Send a test email to verify SMTP configuration."""
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    if not is_email_configured():
        flash(
            "Email service is not configured. Please set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, "
            "SMTP_PASSWORD and MAIL_DEFAULT_SENDER in the environment.",
            "error",
        )
        return redirect(url_for("admin_dashboard"))

    # Send test email to the logged in admin or fallback to default
    admin_user = User.query.get(session.get("user_id"))
    to_email = admin_user.email if admin_user else os.getenv("TEST_EMAIL") or MAIL_DEFAULT_SENDER

    html_body = """
        <p>Hi from <strong>TiffinTrack</strong> 👋</p>
        <p>This is a <strong>test email</strong> to confirm that your email service is configured correctly.</p>
        <p>If you received this, your SMTP settings are working.</p>
    """
    text_body = (
        "Hi from TiffinTrack,\n\n"
        "This is a test email to confirm that your email service is configured correctly.\n"
        "If you received this, your SMTP settings are working."
    )

    success, error = send_email(
        to_email=to_email,
        subject="TiffinTrack – Test Email",
        html_body=html_body,
        text_body=text_body,
    )

    if success:
        flash(f"Test email sent to {to_email}. Please check that inbox.", "success")
    else:
        flash(f"Failed to send test email: {error}", "error")

    return redirect(url_for("admin_dashboard"))

# ---------- Admin Plan Management ----------
@app.route("/admin/plans")
def admin_plans():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    plans = Plan.query.all()
    return render_template("admin_plans.html", plans=plans)

@app.route("/admin/plans/add", methods=["GET", "POST"])
def add_plan():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        daily_rate = request.form.get("daily_rate", "").strip()
        description = request.form.get("description", "").strip()
        items = request.form.getlist("items")
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
                image_filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                file.save(file_path)
                
                # Resize image
                try:
                    resize_image(file_path)
                except Exception as e:
                    print(f"Error resizing image: {e}")
        
        # Validate inputs
        if not name or not daily_rate:
            flash("Name and daily rate are required", "error")
            return render_template("admin_plan_form.html", 
                                 plan=None, 
                                 areas=NAVI_MUMBAI_AREAS)
        
        try:
            daily_rate = int(daily_rate)
        except ValueError:
            flash("Daily rate must be a number", "error")
            return render_template("admin_plan_form.html", 
                                 plan=None, 
                                 areas=NAVI_MUMBAI_AREAS)
        
        # Create new plan
        plan = Plan(
            name=name,
            daily_rate=daily_rate,
            description=description,
            items=json.dumps(items) if items else None,
            image_filename=image_filename
        )
        
        db.session.add(plan)
        db.session.commit()
        
        flash(f"Plan '{name}' created successfully!", "success")
        return redirect(url_for("admin_plans"))
    
    return render_template("admin_plan_form.html", plan=None, areas=NAVI_MUMBAI_AREAS)

@app.route("/admin/plans/edit/<int:plan_id>", methods=["GET", "POST"])
def edit_plan(plan_id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    plan = Plan.query.get_or_404(plan_id)
    
    if request.method == "POST":
        plan.name = request.form.get("name", "").strip()
        plan.description = request.form.get("description", "").strip()
        
        # Update daily rate
        try:
            plan.daily_rate = int(request.form.get("daily_rate", "").strip())
        except ValueError:
            flash("Daily rate must be a number", "error")
            return render_template("admin_plan_form.html", 
                                 plan=plan, 
                                 areas=NAVI_MUMBAI_AREAS)
        
        # Update items
        items = request.form.getlist("items")
        plan.items = json.dumps(items) if items else None
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old image if exists
                if plan.image_filename:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], plan.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new image
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
                plan.image_filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], plan.image_filename)
                file.save(file_path)
                
                # Resize image
                try:
                    resize_image(file_path)
                except Exception as e:
                    print(f"Error resizing image: {e}")
        
        db.session.commit()
        flash(f"Plan '{plan.name}' updated successfully!", "success")
        return redirect(url_for("admin_plans"))
    
    return render_template("admin_plan_form.html", plan=plan, areas=NAVI_MUMBAI_AREAS)

@app.route("/admin/plans/delete/<int:plan_id>", methods=["POST"])
def delete_plan(plan_id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    plan = Plan.query.get_or_404(plan_id)
    
    # Check if plan is being used by customers
    active_subscriptions = CustomerPlan.query.filter_by(plan_id=plan_id, is_active=True).count()
    if active_subscriptions > 0:
        flash(f"Cannot delete plan '{plan.name}' - it has {active_subscriptions} active subscriptions", "error")
        return redirect(url_for("admin_plans"))
    
    # Delete image file if exists
    if plan.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], plan.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    plan_name = plan.name
    db.session.delete(plan)
    db.session.commit()
    
    flash(f"Plan '{plan_name}' deleted successfully!", "success")
    return redirect(url_for("admin_plans"))

@app.route("/admin/plans/toggle/<int:plan_id>", methods=["POST"])
def toggle_plan_status(plan_id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    plan = Plan.query.get_or_404(plan_id)
    plan.is_active = not plan.is_active
    db.session.commit()
    
    status = "activated" if plan.is_active else "deactivated"
    flash(f"Plan '{plan.name}' {status} successfully!", "success")
    return redirect(url_for("admin_plans"))


# ---------- Customer Management ----------
@app.route("/customers")
def customer_management():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    customers = db.session.query(User).filter_by(is_admin=False).all()
    customer_data = []
    
    for customer in customers:
        # Get active plan
        active_plan = db.session.query(CustomerPlan, Plan).select_from(CustomerPlan).join(Plan, CustomerPlan.plan_id == Plan.id).filter(
            CustomerPlan.customer_id == customer.id,
            CustomerPlan.is_active == True
        ).first()
        
        # Check if paused today
        paused_today = PausedDate.query.filter_by(
            customer_id=customer.id,
            pause_date=date.today()
        ).first()
        
        # Get pending bills
        pending_bill = Bill.query.filter_by(
            customer_id=customer.id,
            is_paid=False
        ).first()
        
        customer_data.append({
            'id': customer.id,
            'name': customer.fullname,
            'email': customer.email,
            'phone': customer.phone,
            'area': customer.area,  # Fixed from delivery_area to area
            'plan': active_plan[1].name if active_plan else "No Plan",
            'status': "Paused" if paused_today else "Active",
            'payment': "Pending" if pending_bill else "Paid"
        })
    
    return render_template("customer_management.html", customers=customer_data)


@app.route("/customers/add", methods=["POST"])
def add_customer():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    data = request.get_json()
    
    # Check if email exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already exists'})
    
    # Create new customer
    customer = User(
        fullname=data['fullname'],
        email=data['email'],
        phone=data['phone'],
        password=generate_password_hash("password123"),  # Default password
        addr1=data['addr1'],
        addr2=data.get('addr2', ''),
        city=data['city'],
        state=data['state'],
        pincode=data['pincode'],
        area=data['area'],  # Fixed from delivery_area to area
        is_admin=False
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Customer added successfully'})


# ---------- Kitchen Report ----------
@app.route("/kitchen-report")
def kitchen_report():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    today = date.today()
    
    # Get all active plans for today
    active_plans = db.session.query(CustomerPlan, Plan, User).select_from(CustomerPlan).join(Plan, CustomerPlan.plan_id == Plan.id).join(User, CustomerPlan.customer_id == User.id).filter(
        CustomerPlan.is_active == True,
        CustomerPlan.start_date <= today,
        CustomerPlan.end_date >= today
    ).all()
    
    # Get paused customers for today
    paused_customers = PausedDate.query.filter_by(pause_date=today).all()
    paused_customer_ids = [p.customer_id for p in paused_customers]
    
    # Calculate production requirements
    production_data = {}
    total_meals = 0
    active_customers = 0
    ingredient_summary = {}
    
    for cp, plan, user in active_plans:
        if user.id not in paused_customer_ids:
            active_customers += 1
            if plan.name not in production_data:
                production_data[plan.name] = {
                    'count': 0,
                    'items': json.loads(plan.items) if plan.items else [],
                    'daily_rate': plan.daily_rate
                }
            production_data[plan.name]['count'] += 1
            total_meals += 1
            
            # Calculate ingredient requirements
            items = json.loads(plan.items) if plan.items else []
            for item in items:
                if item not in ingredient_summary:
                    ingredient_summary[item] = 0
                ingredient_summary[item] += 1
    
    # Calculate preparation timeline
    preparation_timeline = [
        {'time': '06:00 AM', 'task': 'Start rice preparation', 'duration': '30 min'},
        {'time': '06:30 AM', 'task': 'Begin dal cooking', 'duration': '45 min'},
        {'time': '07:00 AM', 'task': 'Vegetable preparation', 'duration': '60 min'},
        {'time': '08:00 AM', 'task': 'Roti/bread preparation', 'duration': '45 min'},
        {'time': '09:00 AM', 'task': 'Final assembly & packing', 'duration': '60 min'},
        {'time': '10:00 AM', 'task': 'Quality check & dispatch', 'duration': '30 min'}
    ]
    
    return render_template("kitchen_report.html", 
                         production_data=production_data, 
                         total_meals=total_meals,
                         active_customers=active_customers,
                         paused_today=len(paused_customer_ids),
                         ingredient_summary=ingredient_summary,
                         preparation_timeline=preparation_timeline,
                         report_date=today)


# ---------- Delivery Routes ----------
@app.route("/delivery-routes")
def delivery_routes():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    today = date.today()
    
    # Get all customers with active deliveries today (not paused)
    active_deliveries = db.session.query(User, CustomerPlan, Plan).select_from(CustomerPlan).join(User, CustomerPlan.customer_id == User.id).join(Plan, CustomerPlan.plan_id == Plan.id).filter(
        CustomerPlan.is_active == True,
        CustomerPlan.start_date <= today,
        CustomerPlan.end_date >= today,
        User.is_admin == False
    ).all()
    
    # Get paused customers for today
    paused_customers = PausedDate.query.filter_by(pause_date=today).all()
    paused_customer_ids = [p.customer_id for p in paused_customers]
    
    # Group by delivery area
    routes = {}
    total_deliveries = 0
    
    for user, cp, plan in active_deliveries:
        if user.id not in paused_customer_ids:
            area = user.area
            if area not in routes:
                routes[area] = []
            
            routes[area].append({
                'id': user.id,
                'name': user.fullname,
                'phone': user.phone,
                'address': f"{user.addr1}, {user.addr2 or ''}, {user.city}".strip(', '),
                'plan': plan.name,
                'pincode': user.pincode
            })
            total_deliveries += 1
    
    # Calculate delivery metrics
    estimated_duration = len(routes) * 1.5 if routes else 0  # 1.5 hours per area
    estimated_distance = len(routes) * 8 if routes else 0  # Estimate 8km per area
    
    # Create route statistics for template
    route_stats = {
        'route1': {'deliveries': 0},
        'route2': {'deliveries': 0}, 
        'route3': {'deliveries': 0}
    }
    
    # Distribute areas across routes for display
    area_list = list(routes.keys())
    for i, area in enumerate(area_list):
        route_key = f'route{(i % 3) + 1}'
        route_stats[route_key]['deliveries'] += len(routes[area])
    
    # Sort routes by area name for consistent ordering
    sorted_routes = dict(sorted(routes.items()))
    
    return render_template("delivery_routes.html", 
                         routes=sorted_routes, 
                         total_deliveries=total_deliveries,
                         estimated_duration=round(estimated_duration, 1),
                         estimated_distance=estimated_distance,
                         route_stats=route_stats,
                         delivery_date=today)


# ---------- Bill Management ----------
@app.route("/bills")
def bill_management():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    # Get current month and year
    current_month = date.today().month
    current_year = date.today().year
    
    # Get all bills with customer information
    bills = db.session.query(Bill, User).join(User).order_by(Bill.created_at.desc()).all()
    
    # Calculate billing statistics
    total_bills = len(bills)
    paid_bills = sum(1 for bill, user in bills if bill.is_paid)
    pending_bills = total_bills - paid_bills
    total_revenue = sum(bill.amount for bill, user in bills)
    paid_amount = sum(bill.amount for bill, user in bills if bill.is_paid)
    pending_amount = sum(bill.amount for bill, user in bills if not bill.is_paid)
    
    # Get monthly revenue data for chart
    monthly_revenue = {}
    for bill, user in bills:
        if bill.is_paid:
            month_key = f"{bill.year}-{bill.month:02d}"
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += bill.amount
    
    # Get recent payments (last 10)
    recent_payments = [(bill, user) for bill, user in bills if bill.is_paid][:10]
    
    # Get overdue bills (older than current month)
    overdue_bills = []
    for bill, user in bills:
        if not bill.is_paid:
            bill_date = date(bill.year, bill.month, 1)
            current_date = date(current_year, current_month, 1)
            if bill_date < current_date:
                overdue_bills.append((bill, user))
    
    bill_stats = {
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'pending_bills': pending_bills,
        'total_revenue': total_revenue,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        'overdue_count': len(overdue_bills),
        'collection_rate': round((paid_bills / total_bills * 100) if total_bills > 0 else 0, 1)
    }
    
    return render_template("bill_management.html", 
                         bills=bills,
                         bill_stats=bill_stats,
                         monthly_revenue=monthly_revenue,
                         recent_payments=recent_payments,
                         overdue_bills=overdue_bills,
                         current_month=current_month,
                         current_year=current_year)


@app.route("/bills/generate/<int:month>/<int:year>")
def generate_monthly_bills(month, year):
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    # Get all customers with active plans in that month
    customers = User.query.filter_by(is_admin=False).all()
    
    for customer in customers:
        # Check if bill already exists
        existing_bill = Bill.query.filter_by(
            customer_id=customer.id,
            month=month,
            year=year
        ).first()
        
        if existing_bill:
            continue
        
        # Get customer's active plans for that month
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        active_plans = db.session.query(CustomerPlan, Plan).select_from(CustomerPlan).join(Plan, CustomerPlan.plan_id == Plan.id).filter(
            CustomerPlan.customer_id == customer.id,
            CustomerPlan.is_active == True,
            CustomerPlan.start_date <= last_day,
            CustomerPlan.end_date >= first_day
        ).all()
        
        if not active_plans:
            continue
        
        # Calculate total amount and actual plan days
        total_amount = 0
        actual_plan_days = 0
        total_paused_days = 0
        
        # Calculate amount based on active plans
        for cp, plan in active_plans:
            # Calculate overlap days between plan and billing month
            plan_start = max(cp.start_date, first_day)
            plan_end = min(cp.end_date, last_day)
            
            if plan_start <= plan_end:  # Plan overlaps with this month
                plan_days_in_month = (plan_end - plan_start).days + 1
                actual_plan_days += plan_days_in_month
                
                # Get paused days for this specific plan period in this month
                plan_paused = PausedDate.query.filter(
                    PausedDate.customer_id == customer.id,
                    PausedDate.pause_date >= plan_start,
                    PausedDate.pause_date <= plan_end
                ).count()
                
                total_paused_days += plan_paused
                plan_billable_days = plan_days_in_month - plan_paused
                total_amount += plan_billable_days * plan.daily_rate
        
        # Use actual plan days instead of month days
        total_days = actual_plan_days
        paused_days = total_paused_days
        billable_days = total_days - paused_days
        
        # Create bill
        bill = Bill(
            customer_id=customer.id,
            month=month,
            year=year,
            total_days=total_days,
            paused_days=paused_days,
            billable_days=billable_days,
            amount=total_amount,
            is_paid=False
        )
        
        db.session.add(bill)
    
    db.session.commit()
    flash(f"Bills generated for {month}/{year}", "success")
    return redirect(url_for("bill_management"))


@app.route("/bills/mark-paid/<int:bill_id>")
def mark_bill_paid(bill_id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    bill = Bill.query.get_or_404(bill_id)
    bill.is_paid = True
    db.session.commit()
    
    flash("Bill marked as paid", "success")
    return redirect(url_for("bill_management"))


@app.route("/bills/send-reminders", methods=["POST"])
def send_bill_reminders():
    """Send payment reminders to customers with unpaid bills"""
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Check if email is configured
        if not is_email_configured():
            return jsonify({
                "success": False,
                "error": "Email service is not configured. Please configure SMTP settings in .env file to send reminders."
            }), 400
        
        # Get all unpaid bills
        unpaid_bills = db.session.query(Bill, User).join(User).filter(
            Bill.is_paid == False
        ).all()
        
        if not unpaid_bills:
            return jsonify({
                "success": True,
                "message": "No unpaid bills found. All customers have paid their bills!",
                "sent": 0,
                "failed": 0
            })
        
        sent_count = 0
        failed_count = 0
        errors = []
        
        for bill, user in unpaid_bills:
            # Prepare email content
            subject = f"Payment Reminder - TiffinTrack Bill for {bill.month}/{bill.year}"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #ff6b35;">Payment Reminder</h2>
                    <p>Dear {user.fullname},</p>
                    <p>This is a friendly reminder that you have an unpaid bill for your TiffinTrack meal service.</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Bill Details:</h3>
                        <p><strong>Bill Period:</strong> {bill.month}/{bill.year}</p>
                        <p><strong>Amount Due:</strong> ₹{bill.amount}</p>
                        <p><strong>Days:</strong> {bill.billable_days} days</p>
                    </div>
                    
                    <p>Please log in to your account to make the payment:</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{request.url_root}login" 
                           style="background: #ff6b35; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Pay Now
                        </a>
                    </p>
                    
                    <p>If you have already made the payment, please disregard this reminder.</p>
                    <p>Thank you for choosing TiffinTrack!</p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="font-size: 12px; color: #666;">
                        TiffinTrack - Fresh, Healthy Meals Delivered Daily<br>
                        This is an automated reminder. Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Payment Reminder - TiffinTrack
            
            Dear {user.fullname},
            
            This is a friendly reminder that you have an unpaid bill for your TiffinTrack meal service.
            
            Bill Details:
            - Period: {bill.month}/{bill.year}
            - Amount Due: ₹{bill.amount}
            - Days: {bill.billable_days} days
            
            Please log in to your account to make the payment: {request.url_root}login
            
            If you have already made the payment, please disregard this reminder.
            
            Thank you for choosing TiffinTrack!
            """
            
            # Send email
            success, error = send_email(user.email, subject, html_body, text_body)
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
                errors.append(f"{user.fullname} ({user.email}): {error}")
                print(f"Failed to send reminder to {user.email}: {error}")
        
        # Prepare response message
        if sent_count > 0 and failed_count == 0:
            message = f"Successfully sent {sent_count} reminder(s)!"
        elif sent_count > 0 and failed_count > 0:
            message = f"Sent {sent_count} reminder(s), but {failed_count} failed"
        else:
            message = f"Failed to send all {failed_count} reminder(s)"
        
        return jsonify({
            "success": sent_count > 0,
            "message": message,
            "sent": sent_count,
            "failed": failed_count,
            "errors": errors[:5] if errors else []  # Return first 5 errors
        })
        
    except Exception as e:
        print(f"Error sending reminders: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to send reminders: {str(e)}"
        }), 500


@app.route("/bills/export")
def export_bills():
    """Export billing data to CSV"""
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    try:
        import csv
        from io import StringIO
        
        # Get filter parameters
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        status = request.args.get('status')  # 'paid', 'unpaid', or 'all'
        
        # Build query
        query = db.session.query(Bill, User).join(User)
        
        if month:
            query = query.filter(Bill.month == month)
        if year:
            query = query.filter(Bill.year == year)
        if status == 'paid':
            query = query.filter(Bill.is_paid == True)
        elif status == 'unpaid':
            query = query.filter(Bill.is_paid == False)
        
        bills = query.order_by(Bill.created_at.desc()).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Bill ID',
            'Customer Name',
            'Customer Email',
            'Customer Phone',
            'Customer Area',
            'Month',
            'Year',
            'Total Days',
            'Paused Days',
            'Billable Days',
            'Amount (₹)',
            'Status',
            'Created Date',
            'Payment Date'
        ])
        
        # Write data
        for bill, user in bills:
            writer.writerow([
                bill.id,
                user.fullname,
                user.email,
                user.phone,
                user.area,
                bill.month,
                bill.year,
                bill.total_days,
                bill.paused_days,
                bill.billable_days,
                bill.amount,
                'Paid' if bill.is_paid else 'Unpaid',
                bill.created_at.strftime('%Y-%m-%d %H:%M:%S') if bill.created_at else '',
                bill.updated_at.strftime('%Y-%m-%d %H:%M:%S') if bill.is_paid and bill.updated_at else ''
            ])
        
        # Prepare response
        output.seek(0)
        filename = f"tiffintrack_bills_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        print(f"Error exporting bills: {e}")
        flash("Failed to export bills", "error")
        return redirect(url_for("bill_management"))


# ---------- Stripe Payment Integration ----------
@app.route("/pay-bill/<int:bill_id>")
def pay_bill(bill_id):
    """Display payment page for a specific bill"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    customer_id = session["user_id"]
    bill = db.session.query(Bill, User).join(User).filter(
        Bill.id == bill_id,
        Bill.customer_id == customer_id,
        Bill.is_paid == False
    ).first()
    
    if not bill:
        flash("Bill not found or already paid", "error")
        return redirect(url_for("customer_dashboard"))
    
    bill_obj, user = bill
    
    return render_template("payment.html", 
                         bill=bill_obj,
                         user=user,
                         stripe_publishable_key=app.config["STRIPE_PUBLISHABLE_KEY"])


# ---------- Analytics Dashboard ----------
@app.route("/analytics")
def analytics_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    # Get date range (default to last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    date_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    
    # Calculate key metrics
    total_customers = User.query.filter_by(is_admin=False).count()
    active_customers = db.session.query(CustomerPlan).filter(
        CustomerPlan.is_active == True,
        CustomerPlan.end_date >= date.today()
    ).distinct(CustomerPlan.customer_id).count()
    
    # Revenue calculations
    total_revenue = db.session.query(db.func.sum(Bill.amount)).filter(
        Bill.is_paid == True
    ).scalar() or 0
    
    monthly_revenue = db.session.query(db.func.sum(Bill.amount)).filter(
        Bill.is_paid == True,
        Bill.month == end_date.month,
        Bill.year == end_date.year
    ).scalar() or 0
    
    # Calculate growth rates (comparing to previous period)
    prev_month = end_date.month - 1 if end_date.month > 1 else 12
    prev_year = end_date.year if end_date.month > 1 else end_date.year - 1
    
    prev_monthly_revenue = db.session.query(db.func.sum(Bill.amount)).filter(
        Bill.is_paid == True,
        Bill.month == prev_month,
        Bill.year == prev_year
    ).scalar() or 0
    
    revenue_growth = round(((monthly_revenue - prev_monthly_revenue) / prev_monthly_revenue * 100) if prev_monthly_revenue > 0 else 0, 1)
    
    # Customer growth
    prev_month_customers = db.session.query(CustomerPlan).filter(
        CustomerPlan.created_at < date(end_date.year, end_date.month, 1)
    ).distinct(CustomerPlan.customer_id).count()
    
    customer_growth = round(((active_customers - prev_month_customers) / prev_month_customers * 100) if prev_month_customers > 0 else 0, 1)
    
    # Meal statistics
    total_meals = db.session.query(CustomerPlan).filter(
        CustomerPlan.is_active == True
    ).count() * 30  # Approximate monthly meals
    
    meals_growth = 12.5  # Mock data
    
    avg_order_value = round(total_revenue / total_customers if total_customers > 0 else 0, 2)
    
    # Plan popularity
    plan_popularity = db.session.query(
        Plan.name, 
        db.func.count(CustomerPlan.id).label('count')
    ).select_from(Plan).join(CustomerPlan, Plan.id == CustomerPlan.plan_id).filter(
        CustomerPlan.is_active == True
    ).group_by(Plan.name).all()
    
    # Create plan distribution data for charts
    plan_labels = [plan_name for plan_name, count in plan_popularity]
    plan_data = [count for plan_name, count in plan_popularity]
    total_plans = sum(plan_data) if plan_data else 1
    plan_distribution = [
        {
            'name': plan_name,
            'percentage': round((count / total_plans) * 100, 1),
            'color': ['#ff6b35', '#4ecdc4', '#ffd54f', '#3b82f6'][i % 4]
        }
        for i, (plan_name, count) in enumerate(plan_popularity)
    ]
    
    # Area-wise distribution
    area_distribution = db.session.query(
        User.area,
        db.func.count(User.id).label('count')
    ).filter(User.is_admin == False).group_by(User.area).all()
    
    # Create area performance data
    area_performance = []
    total_area_revenue = sum(monthly_revenue / len(area_distribution) for area, count in area_distribution) if area_distribution else 0
    
    for area, count in area_distribution:
        area_revenue = (monthly_revenue / len(area_distribution)) if area_distribution else 0
        area_performance.append({
            'name': area,
            'customers': count,
            'revenue': round(area_revenue),
            'percentage': round((area_revenue / monthly_revenue * 100) if monthly_revenue > 0 else 0, 1)
        })
    
    # Monthly revenue trend (last 6 months)
    revenue_trend = []
    revenue_labels = []
    revenue_data = []
    
    for i in range(6):
        month_date = end_date - timedelta(days=30*i)
        month_revenue = db.session.query(db.func.sum(Bill.amount)).filter(
            Bill.is_paid == True,
            Bill.month == month_date.month,
            Bill.year == month_date.year
        ).scalar() or 0
        revenue_trend.append({
            'month': month_date.strftime('%B'),
            'revenue': month_revenue
        })
        revenue_labels.append(month_date.strftime('%b'))
        revenue_data.append(month_revenue)
    
    revenue_trend.reverse()
    revenue_labels.reverse()
    revenue_data.reverse()
    
    # Customer growth data (last 6 months)
    customer_labels = []
    customer_data = []
    
    for i in range(6):
        month_date = end_date - timedelta(days=30*i)
        new_customers = User.query.filter(
            User.is_admin == False,
            db.extract('month', User.created_at) == month_date.month,
            db.extract('year', User.created_at) == month_date.year
        ).count()
        customer_labels.append(month_date.strftime('%b'))
        customer_data.append(new_customers)
    
    customer_labels.reverse()
    customer_data.reverse()
    
    # Customer retention rate
    total_active_plans = CustomerPlan.query.filter_by(is_active=True).count()
    retention_rate = round((total_active_plans / total_customers * 100) if total_customers > 0 else 0, 1)
    retention_growth = 5.2  # Mock data
    
    # Operational metrics (mock data for demonstration)
    delivery_success_rate = 96.8
    pause_rate = 8.5
    customer_satisfaction = 4.7
    food_waste = 15.2
    collection_efficiency = round((db.session.query(Bill).filter_by(is_paid=True).count() / db.session.query(Bill).count() * 100) if db.session.query(Bill).count() > 0 else 0, 1)
    
    # AI-powered insights (mock data)
    insights = [
        {
            'title': 'Peak Demand Optimization',
            'category': 'Operations',
            'description': 'Consider increasing kitchen capacity during 12-2 PM to handle 35% higher demand during lunch hours.',
            'impact': '+12% efficiency',
            'timeframe': 'Next 2 weeks',
            'icon': 'fas fa-chart-line',
            'bg_color': 'var(--success-light)',
            'border_color': 'var(--success)',
            'icon_color': 'var(--success)',
            'text_color': 'var(--success-dark)',
            'impact_color': 'var(--success)'
        },
        {
            'title': 'Customer Retention Strategy',
            'category': 'Marketing',
            'description': 'Customers in Kharghar area show 23% higher retention. Apply similar engagement strategies to other areas.',
            'impact': '+8% retention',
            'timeframe': 'Next month',
            'icon': 'fas fa-users',
            'bg_color': 'var(--info-light)',
            'border_color': 'var(--info)',
            'icon_color': 'var(--info)',
            'text_color': 'var(--info-dark)',
            'impact_color': 'var(--info)'
        },
        {
            'title': 'Revenue Growth Opportunity',
            'category': 'Finance',
            'description': 'Diet Special plan shows highest profit margin. Promote this plan to increase overall revenue by 15%.',
            'impact': '+₹25K monthly',
            'timeframe': 'Next quarter',
            'icon': 'fas fa-rupee-sign',
            'bg_color': 'var(--warning-light)',
            'border_color': 'var(--warning)',
            'icon_color': 'var(--warning)',
            'text_color': 'var(--warning-dark)',
            'impact_color': 'var(--warning)'
        }
    ]
    
    analytics_data = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'revenue_growth': revenue_growth,
        'active_customers': active_customers,
        'customer_growth': customer_growth,
        'total_meals': total_meals,
        'meals_growth': meals_growth,
        'avg_order_value': avg_order_value,
        'plan_popularity': plan_popularity,
        'plan_distribution': plan_distribution,
        'plan_labels': plan_labels,
        'plan_data': plan_data,
        'area_distribution': area_distribution,
        'area_performance': area_performance,
        'revenue_trend': revenue_trend,
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'customer_labels': customer_labels,
        'customer_data': customer_data,
        'retention_rate': retention_rate,
        'retention_growth': retention_growth,
        'total_customers': total_customers,
        'delivery_success_rate': delivery_success_rate,
        'pause_rate': pause_rate,
        'customer_satisfaction': customer_satisfaction,
        'food_waste': food_waste,
        'collection_efficiency': collection_efficiency,
        'insights': insights
    }
    
    return render_template("analytics.html", 
                         analytics=analytics_data,
                         date_range=date_range)


@app.route("/dashboard")
@db_retry(max_retries=3, delay=1)
def customer_dashboard():
    if "user_id" not in session or session.get("is_admin"):
        return redirect(url_for("login"))
    
    customer_id = session["user_id"]
    
    # Check for payment success message
    payment_success = request.args.get('payment') == 'success'
    recent_payment = None
    
    if payment_success:
        # Get the most recent successful payment for this customer
        recent_payment = db.session.query(Payment, Bill).join(Bill).filter(
            Payment.customer_id == customer_id,
            Payment.status == 'succeeded'
        ).order_by(Payment.updated_at.desc()).first()
    
    try:
        # Get customer's active plans (not expired)
        active_plans = db.session.query(CustomerPlan, Plan).select_from(CustomerPlan).join(Plan, CustomerPlan.plan_id == Plan.id).filter(
            CustomerPlan.customer_id == customer_id,
            CustomerPlan.is_active == True,
            CustomerPlan.end_date >= date.today()
        ).order_by(CustomerPlan.end_date.asc()).all()
        
        # Get upcoming plans (not started yet)
        upcoming_plans = [
            (cp, plan) for cp, plan in active_plans 
            if cp.start_date > date.today()
        ]
        
        # Get currently running plans
        running_plans = [
            (cp, plan) for cp, plan in active_plans 
            if cp.start_date <= date.today() <= cp.end_date
        ]
        
        # Get current month's paused days
        current_month = date.today().month
        current_year = date.today().year
        paused_this_month = PausedDate.query.filter(
            PausedDate.customer_id == customer_id,
            db.extract('month', PausedDate.pause_date) == current_month,
            db.extract('year', PausedDate.pause_date) == current_year
        ).count()
        
        # Calculate estimated bill for current month and total plan days
        estimated_bill = 0
        total_plan_days = 0
        current_month_start = date(current_year, current_month, 1)
        current_month_end = date(current_year, current_month, monthrange(current_year, current_month)[1])
        
        for cp, plan in active_plans:
            # Calculate overlap with current month
            plan_start = max(cp.start_date, current_month_start)
            plan_end = min(cp.end_date, current_month_end)
            
            if plan_start <= plan_end:
                plan_days = (plan_end - plan_start).days + 1
                total_plan_days += plan_days
                
                # Get paused days for this specific plan period
                plan_paused = PausedDate.query.filter(
                    PausedDate.customer_id == customer_id,
                    PausedDate.pause_date >= plan_start,
                    PausedDate.pause_date <= plan_end
                ).count()
                
                billable_days = plan_days - plan_paused
                estimated_bill += billable_days * plan.daily_rate
        
        # Get recent activity
        recent_pauses = PausedDate.query.filter_by(customer_id=customer_id).order_by(
            PausedDate.created_at.desc()
        ).limit(5).all()
        
        # Check if paused today
        paused_today = PausedDate.query.filter_by(
            customer_id=customer_id,
            pause_date=date.today()
        ).first() is not None
        
        # Get customer's bills for payment (separate paid and unpaid)
        all_bills = Bill.query.filter_by(customer_id=customer_id).order_by(Bill.created_at.desc()).all()
        unpaid_bills = [bill for bill in all_bills if not bill.is_paid]
        paid_bills = [bill for bill in all_bills if bill.is_paid]
        
        # Get recent payments for history
        recent_payments = db.session.query(Payment, Bill).join(Bill).filter(
            Payment.customer_id == customer_id,
            Payment.status == 'succeeded'
        ).order_by(Payment.updated_at.desc()).limit(5).all()
        
        dashboard_data = {
            'active_plans': active_plans,
            'running_plans': running_plans,
            'upcoming_plans': upcoming_plans,
            'estimated_bill': estimated_bill,
            'paused_this_month': paused_this_month,
            'recent_pauses': recent_pauses,
            'paused_today': paused_today,
            'total_days': total_plan_days,  # Use actual plan days instead of month days
            'billable_days': total_plan_days - paused_this_month,
            'bills': unpaid_bills,  # Only show unpaid bills in pending section
            'paid_bills': paid_bills,
            'recent_payments': recent_payments,
            'payment_success': payment_success,
            'recent_payment': recent_payment,
            'date': date  # Pass date class for template calculations
        }
        
        return render_template("customer_dashboard.html", **dashboard_data)
        
    except Exception as e:
        print(f"❌ Error in customer dashboard: {e}")
        flash("Temporary database connection issue. Please try again.", "error")
        return redirect(url_for("login"))


@app.route("/pause")
def pause_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    paused = PausedDate.query.filter_by(customer_id=session["user_id"]).all()
    paused_dates = [p.pause_date.strftime("%Y-%m-%d") for p in paused]

    return render_template("pause_calendar.html", 
                         paused_dates=paused_dates,
                         date=date,
                         timedelta=timedelta)


@app.route("/pause/save", methods=["POST"])
def save_pause():
    if "user_id" not in session:
        return redirect(url_for("login"))

    selected_date = request.form.get("pause_date")
    pause_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    # Cutoff time validation (8:00 AM)
    cutoff_time = time(8, 0)  # 8:00 AM
    current_time = datetime.now().time()
    
    if pause_date == date.today() and current_time > cutoff_time:
        flash("Cannot pause today's meal after 8:00 AM cutoff time", "error")
        return redirect(url_for("pause_page"))

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


@app.route("/pause/remove", methods=["POST"])
def remove_pause():
    """Remove a paused date"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        pause_date_str = data.get("pause_date")

        if not pause_date_str:
            return jsonify({"error": "Date required"}), 400

        pause_date = datetime.strptime(pause_date_str, "%Y-%m-%d").date()

        # Find and delete the paused date
        paused = PausedDate.query.filter_by(
            customer_id=session["user_id"],
            pause_date=pause_date
        ).first()

        if not paused:
            return jsonify({"error": "Paused date not found"}), 404

        # Check if it's too late to remove (after 8 AM on the pause date)
        cutoff_time = time(8, 0)
        current_time = datetime.now().time()

        if pause_date == date.today() and current_time > cutoff_time:
            return jsonify({"error": "Cannot remove pause after 8:00 AM cutoff time"}), 400

        if pause_date < date.today():
            return jsonify({"error": "Cannot remove pause for past dates"}), 400

        db.session.delete(paused)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Pause removed successfully"
        })

    except Exception as e:
        print(f"Error removing pause: {e}")
        return jsonify({"error": "Failed to remove pause"}), 500



# ---------- Plans ----------
@app.route("/plans")
def choose_plans():
    if "user_id" not in session:
        return redirect(url_for("login"))

    plans = Plan.query.filter_by(is_active=True).all()
    return render_template("choose_plans.html", plans=plans, date=date)


@app.route("/plans/cancel/<int:plan_id>", methods=["POST"])
def cancel_plan(plan_id):
    """Cancel an individual customer plan"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        customer_id = session["user_id"]
        
        # Find the customer plan
        customer_plan = CustomerPlan.query.filter_by(
            id=plan_id,
            customer_id=customer_id
        ).first()
        
        if not customer_plan:
            return jsonify({"error": "Plan not found"}), 404
        
        # Check if plan has already started
        if customer_plan.start_date <= date.today():
            return jsonify({"error": "Cannot cancel a plan that has already started"}), 400
        
        # Delete the plan
        db.session.delete(customer_plan)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Plan cancelled successfully"
        })
        
    except Exception as e:
        print(f"Error cancelling plan: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to cancel plan"}), 500


@app.route("/plans/save", methods=["POST"])
def save_plans():
    if "user_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["user_id"]
    
    # Collect selected plans
    selected_plans = []
    total_cost = 0
    
    for key in request.form:
        if key.startswith("plan_") and request.form.get(key) == "1":
            plan_id = int(key.split("_")[1])
            start_date_str = request.form.get(f"start_{plan_id}")
            end_date_str = request.form.get(f"end_{plan_id}")

            if not start_date_str or not end_date_str:
                flash("Please select valid dates for all plans", "error")
                return redirect(url_for("choose_plans"))

            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format", "error")
                return redirect(url_for("choose_plans"))

            # Validate date range
            if end_date < start_date:
                flash("End date cannot be before start date", "error")
                return redirect(url_for("choose_plans"))
            
            # Allow plans to start today or in the future
            if start_date < date.today():
                flash("Start date cannot be in the past", "error")
                return redirect(url_for("choose_plans"))
            
            # Provide helpful feedback about when plan starts
            if start_date == date.today():
                plan_start_msg = "starts today"
            elif start_date == date.today() + timedelta(days=1):
                plan_start_msg = "starts tomorrow"
            else:
                plan_start_msg = f"starts on {start_date.strftime('%B %d, %Y')}"
            
            # Get plan details for cost calculation
            plan = Plan.query.get(plan_id)
            if not plan:
                flash("Invalid plan selected", "error")
                return redirect(url_for("choose_plans"))
            
            # Calculate duration and cost
            duration_days = (end_date - start_date).days + 1
            plan_cost = duration_days * plan.daily_rate
            total_cost += plan_cost
            
            selected_plans.append({
                'plan_id': plan_id,
                'plan_name': plan.name,
                'start_date': start_date,
                'end_date': end_date,
                'duration_days': duration_days,
                'daily_rate': plan.daily_rate,
                'total_cost': plan_cost,
                'start_msg': plan_start_msg
            })
    
    if not selected_plans:
        flash("Please select at least one plan", "error")
        return redirect(url_for("choose_plans"))
    
    # Check for overlapping plans (same plan with overlapping dates)
    for i, plan1 in enumerate(selected_plans):
        for j, plan2 in enumerate(selected_plans):
            if i != j and plan1['plan_id'] == plan2['plan_id']:
                # Check for date overlap
                if (plan1['start_date'] <= plan2['end_date'] and 
                    plan1['end_date'] >= plan2['start_date']):
                    flash(f"Cannot select overlapping dates for the same plan: {plan1['plan_name']}", "error")
                    return redirect(url_for("choose_plans"))
    
    # Remove existing active plans for this customer
    CustomerPlan.query.filter_by(customer_id=customer_id, is_active=True).delete()
    db.session.commit()
    
    # Add new plans
    for plan_data in selected_plans:
        customer_plan = CustomerPlan(
            customer_id=customer_id,
            plan_id=plan_data['plan_id'],
            start_date=plan_data['start_date'],
            end_date=plan_data['end_date'],
            is_active=True
        )
        db.session.add(customer_plan)
    
    db.session.commit()
    
    # Create success message with summary
    if len(selected_plans) == 1:
        plan = selected_plans[0]
        flash(f"Successfully subscribed to {plan['plan_name']} for {plan['duration_days']} days (₹{plan['total_cost']}) - {plan['start_msg']}", "success")
    else:
        flash(f"Successfully subscribed to {len(selected_plans)} plans. Total cost: ₹{total_cost}", "success")
    
    return redirect(url_for("customer_dashboard"))


@app.route("/plans/customize")
def customize_plans():
    """Step 2: Customize plan durations"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    return render_template("customize_plans.html")


@app.route("/plans/checkout")
def plan_checkout():
    """Step 3: Checkout and payment for plans"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    return render_template("plan_checkout.html", stripe_publishable_key=stripe_publishable_key)


@app.route("/plans/process-payment", methods=["POST"])
def process_plan_payment():
    """Process payment for plan subscription"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        configurations = data.get("configurations")
        
        if not configurations:
            return jsonify({"error": "No plan configurations provided"}), 400
        
        customer_id = session["user_id"]
        total_amount = 0
        
        # Calculate total and validate
        for config in configurations:
            total_amount += config['totalCost']
        
        # Create Stripe Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Convert to paise
            currency="inr",
            metadata={
                "customer_id": customer_id,
                "type": "plan_subscription",
                "plan_count": len(configurations)
            },
            description=f"TiffinTrack Plan Subscription - {len(configurations)} plan(s)"
        )
        
        # Store configurations in session for later processing
        session['pending_plan_configs'] = configurations
        
        return jsonify({
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        })
        
    except Exception as e:
        print(f"Error creating payment intent: {e}")
        return jsonify({"error": "Failed to create payment intent"}), 500


@app.route("/plans/payment-success", methods=["POST"])
def plan_payment_success():
    """Handle successful plan payment"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        payment_intent_id = data.get("payment_intent_id")
        
        if not payment_intent_id:
            return jsonify({"error": "Payment Intent ID required"}), 400
        
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == "succeeded":
            customer_id = session["user_id"]
            configurations = session.get('pending_plan_configs', [])
            
            if not configurations:
                return jsonify({"error": "No pending configurations found"}), 404
            
            # Get customer details
            customer = User.query.get(customer_id)
            if not customer:
                return jsonify({"error": "Customer not found"}), 404
            
            # Add new plans (keep existing active plans running)
            new_plans = []
            total_amount_paid = 0
            
            for config in configurations:
                customer_plan = CustomerPlan(
                    customer_id=customer_id,
                    plan_id=config['planId'],
                    start_date=datetime.strptime(config['startDate'], "%Y-%m-%d").date(),
                    end_date=datetime.strptime(config['endDate'], "%Y-%m-%d").date(),
                    is_active=True
                )
                db.session.add(customer_plan)
                
                # Get plan details for receipt
                plan = Plan.query.get(config['planId'])
                total_cost = config.get('totalCost', 0)
                total_amount_paid += total_cost
                
                new_plans.append({
                    'plan_id': config['planId'],
                    'plan_name': plan.name if plan else 'Unknown Plan',
                    'start_date': datetime.strptime(config['startDate'], "%Y-%m-%d").date(),
                    'end_date': datetime.strptime(config['endDate'], "%Y-%m-%d").date(),
                    'amount': total_cost,
                    'days': (datetime.strptime(config['endDate'], "%Y-%m-%d").date() - 
                            datetime.strptime(config['startDate'], "%Y-%m-%d").date()).days + 1
                })
            
            db.session.flush()  # Flush to get IDs
            
            # Create bills for each plan period
            created_bills = []
            for plan_info in new_plans:
                start_date = plan_info['start_date']
                end_date = plan_info['end_date']
                plan_id = plan_info['plan_id']
                
                # Get plan details
                plan = Plan.query.get(plan_id)
                if not plan:
                    continue
                
                # Calculate total days
                total_days = (end_date - start_date).days + 1
                
                # Get paused days (if any)
                paused_days = PausedDate.query.filter(
                    PausedDate.customer_id == customer_id,
                    PausedDate.pause_date >= start_date,
                    PausedDate.pause_date <= end_date
                ).count()
                
                billable_days = total_days - paused_days
                amount = billable_days * plan.daily_rate
                
                # Determine which month(s) this plan covers
                current_date = start_date
                while current_date <= end_date:
                    month = current_date.month
                    year = current_date.year
                    
                    # Check if bill already exists for this month
                    existing_bill = Bill.query.filter_by(
                        customer_id=customer_id,
                        month=month,
                        year=year
                    ).first()
                    
                    # Calculate days in this month
                    month_start = date(year, month, 1)
                    month_end = date(year, month, monthrange(year, month)[1])
                    
                    period_start = max(start_date, month_start)
                    period_end = min(end_date, month_end)
                    
                    if period_start <= period_end:
                        month_days = (period_end - period_start).days + 1
                        
                        # Get paused days for this month
                        month_paused = PausedDate.query.filter(
                            PausedDate.customer_id == customer_id,
                            PausedDate.pause_date >= period_start,
                            PausedDate.pause_date <= period_end
                        ).count()
                        
                        month_billable = month_days - month_paused
                        month_amount = month_billable * plan.daily_rate
                        
                        if existing_bill:
                            # Update existing bill
                            existing_bill.total_days += month_days
                            existing_bill.paused_days += month_paused
                            existing_bill.billable_days += month_billable
                            existing_bill.amount += month_amount
                            existing_bill.is_paid = True  # Mark as paid since payment was successful
                            created_bills.append({
                                'month': month,
                                'year': year,
                                'amount': existing_bill.amount
                            })
                        else:
                            # Create new bill
                            bill = Bill(
                                customer_id=customer_id,
                                month=month,
                                year=year,
                                total_days=month_days,
                                paused_days=month_paused,
                                billable_days=month_billable,
                                amount=month_amount,
                                is_paid=True  # Mark as paid since payment was successful
                            )
                            db.session.add(bill)
                            created_bills.append({
                                'month': month,
                                'year': year,
                                'amount': month_amount
                            })
                    
                    # Move to next month
                    if month == 12:
                        current_date = date(year + 1, 1, 1)
                    else:
                        current_date = date(year, month + 1, 1)
            
            db.session.commit()
            
            # Send receipt email
            if is_email_configured():
                try:
                    # Prepare receipt email
                    subject = f"Payment Receipt - TiffinTrack Order Confirmation"
                    
                    # Build plan details HTML
                    plans_html = ""
                    for idx, plan_info in enumerate(new_plans, 1):
                        plans_html += f"""
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 12px; text-align: left;">{idx}</td>
                            <td style="padding: 12px; text-align: left;">
                                <strong>{plan_info['plan_name']}</strong><br>
                                <span style="color: #666; font-size: 13px;">
                                    {plan_info['start_date'].strftime('%b %d, %Y')} - {plan_info['end_date'].strftime('%b %d, %Y')}
                                </span>
                            </td>
                            <td style="padding: 12px; text-align: center;">{plan_info['days']} days</td>
                            <td style="padding: 12px; text-align: right; font-weight: 600;">₹{plan_info['amount']}</td>
                        </tr>
                        """
                    
                    html_body = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px;">
                        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <div style="background: linear-gradient(135deg, #ff6b35 0%, #ff8c61 100%); padding: 30px; text-align: center; color: white;">
                                <h1 style="margin: 0; font-size: 28px;">Payment Successful! 🎉</h1>
                                <p style="margin: 10px 0 0 0; opacity: 0.9;">Thank you for your order</p>
                            </div>
                            
                            <!-- Content -->
                            <div style="padding: 30px;">
                                <p style="font-size: 16px; margin-bottom: 20px;">Dear {customer.fullname},</p>
                                
                                <p style="margin-bottom: 25px;">
                                    Your payment has been successfully processed! Your meal plan(s) are now active and ready to go.
                                </p>
                                
                                <!-- Receipt Details -->
                                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                                    <h3 style="margin: 0 0 15px 0; color: #ff6b35; font-size: 18px;">Receipt Details</h3>
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr style="border-bottom: 1px solid #ddd;">
                                            <td style="padding: 8px 0; color: #666;">Transaction ID:</td>
                                            <td style="padding: 8px 0; text-align: right; font-weight: 600;">{payment_intent_id[:20]}...</td>
                                        </tr>
                                        <tr style="border-bottom: 1px solid #ddd;">
                                            <td style="padding: 8px 0; color: #666;">Date:</td>
                                            <td style="padding: 8px 0; text-align: right; font-weight: 600;">{datetime.now().strftime('%b %d, %Y %I:%M %p')}</td>
                                        </tr>
                                        <tr style="border-bottom: 1px solid #ddd;">
                                            <td style="padding: 8px 0; color: #666;">Payment Method:</td>
                                            <td style="padding: 8px 0; text-align: right; font-weight: 600;">Card Payment</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; color: #666;">Status:</td>
                                            <td style="padding: 8px 0; text-align: right;">
                                                <span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">PAID</span>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                                
                                <!-- Order Summary -->
                                <h3 style="margin: 0 0 15px 0; color: #333; font-size: 18px;">Order Summary</h3>
                                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; border: 1px solid #eee; border-radius: 8px; overflow: hidden;">
                                    <thead>
                                        <tr style="background: #f8f9fa;">
                                            <th style="padding: 12px; text-align: left; font-weight: 600; color: #666;">#</th>
                                            <th style="padding: 12px; text-align: left; font-weight: 600; color: #666;">Plan Details</th>
                                            <th style="padding: 12px; text-align: center; font-weight: 600; color: #666;">Duration</th>
                                            <th style="padding: 12px; text-align: right; font-weight: 600; color: #666;">Amount</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {plans_html}
                                        <tr style="background: #f8f9fa;">
                                            <td colspan="3" style="padding: 15px; text-align: right; font-weight: 700; font-size: 16px;">Total Paid:</td>
                                            <td style="padding: 15px; text-align: right; font-weight: 700; font-size: 18px; color: #ff6b35;">₹{total_amount_paid}</td>
                                        </tr>
                                    </tbody>
                                </table>
                                
                                <!-- Next Steps -->
                                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; border-left: 4px solid #10b981; margin-bottom: 25px;">
                                    <h4 style="margin: 0 0 10px 0; color: #047857;">What's Next?</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #065f46;">
                                        <li style="margin-bottom: 8px;">Your meal deliveries will start as per your selected dates</li>
                                        <li style="margin-bottom: 8px;">You can pause meals anytime from your dashboard</li>
                                        <li style="margin-bottom: 8px;">View your bills and payment history in the billing section</li>
                                    </ul>
                                </div>
                                
                                <!-- CTA Button -->
                                <div style="text-align: center; margin: 30px 0;">
                                    <a href="{request.url_root}dashboard" 
                                       style="display: inline-block; background: #ff6b35; color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                                        View Dashboard
                                    </a>
                                </div>
                                
                                <p style="color: #666; font-size: 14px; margin-top: 25px;">
                                    If you have any questions or concerns, please don't hesitate to contact us.
                                </p>
                                
                                <p style="margin-top: 20px;">
                                    Best regards,<br>
                                    <strong>TiffinTrack Team</strong>
                                </p>
                            </div>
                            
                            <!-- Footer -->
                            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                                <p style="margin: 0; font-size: 12px; color: #666;">
                                    TiffinTrack - Fresh, Healthy Meals Delivered Daily<br>
                                    This is an automated receipt. Please do not reply to this email.
                                </p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    text_body = f"""
                    Payment Receipt - TiffinTrack
                    
                    Dear {customer.fullname},
                    
                    Your payment has been successfully processed!
                    
                    Receipt Details:
                    - Transaction ID: {payment_intent_id}
                    - Date: {datetime.now().strftime('%b %d, %Y %I:%M %p')}
                    - Payment Method: Card Payment
                    - Status: PAID
                    
                    Order Summary:
                    """
                    
                    for idx, plan_info in enumerate(new_plans, 1):
                        text_body += f"""
                    {idx}. {plan_info['plan_name']}
                       Period: {plan_info['start_date'].strftime('%b %d, %Y')} - {plan_info['end_date'].strftime('%b %d, %Y')}
                       Duration: {plan_info['days']} days
                       Amount: ₹{plan_info['amount']}
                    """
                    
                    text_body += f"""
                    
                    Total Paid: ₹{total_amount_paid}
                    
                    What's Next?
                    - Your meal deliveries will start as per your selected dates
                    - You can pause meals anytime from your dashboard
                    - View your bills and payment history in the billing section
                    
                    View your dashboard: {request.url_root}dashboard
                    
                    Thank you for choosing TiffinTrack!
                    
                    Best regards,
                    TiffinTrack Team
                    """
                    
                    # Send email
                    send_email(customer.email, subject, html_body, text_body)
                    print(f"✅ Receipt email sent to {customer.email}")
                    
                except Exception as email_error:
                    print(f"⚠️ Failed to send receipt email: {email_error}")
                    # Don't fail the whole transaction if email fails
            
            # Clear pending configurations
            session.pop('pending_plan_configs', None)
            
            return jsonify({
                "success": True,
                "message": "Plans activated and bills created successfully!",
                "redirect_url": url_for("payment_success", payment_intent_id=payment_intent_id, _external=False)
            })
        else:
            return jsonify({"error": "Payment not completed"}), 400
            
    except Exception as e:
        print(f"Error processing plan payment: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Failed to process payment"}), 500


# ---------- Billing ----------
@app.route("/billing")
@db_retry(max_retries=3, delay=1)
def billing_page():
    """Display customer billing page with all bills and payment history"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    customer_id = session["user_id"]
    
    try:
        # Get all bills
        all_bills = Bill.query.filter_by(customer_id=customer_id).order_by(Bill.created_at.desc()).all()
        unpaid_bills = [bill for bill in all_bills if not bill.is_paid]
        paid_bills = [bill for bill in all_bills if bill.is_paid]
        
        # Calculate total due
        total_due = sum(bill.amount for bill in unpaid_bills)
        
        # Get current month's estimated bill
        current_month = date.today().month
        current_year = date.today().year
        
        # Get customer's active plans
        active_plans = db.session.query(CustomerPlan, Plan).select_from(CustomerPlan).join(
            Plan, CustomerPlan.plan_id == Plan.id
        ).filter(
            CustomerPlan.customer_id == customer_id,
            CustomerPlan.is_active == True,
            CustomerPlan.end_date >= date.today()
        ).all()
        
        # Calculate estimated bill for current month
        estimated_bill = 0
        current_month_start = date(current_year, current_month, 1)
        current_month_end = date(current_year, current_month, monthrange(current_year, current_month)[1])
        
        for cp, plan in active_plans:
            plan_start = max(cp.start_date, current_month_start)
            plan_end = min(cp.end_date, current_month_end)
            
            if plan_start <= plan_end:
                plan_days = (plan_end - plan_start).days + 1
                
                # Get paused days
                plan_paused = PausedDate.query.filter(
                    PausedDate.customer_id == customer_id,
                    PausedDate.pause_date >= plan_start,
                    PausedDate.pause_date <= plan_end
                ).count()
                
                billable_days = plan_days - plan_paused
                estimated_bill += billable_days * plan.daily_rate
        
        return render_template("billing.html",
                             unpaid_bills=unpaid_bills,
                             paid_bills=paid_bills,
                             total_due=total_due,
                             estimated_bill=estimated_bill)
    
    except Exception as e:
        print(f"❌ Error in billing page: {e}")
        flash("Error loading billing information. Please try again.", "error")
        return redirect(url_for("customer_dashboard"))

@app.route("/terms")
def terms():
    return render_template("terms.html")


# ---------- Stripe Payment Integration ----------
@app.route("/payment/<int:bill_id>")
def payment_page(bill_id):
    """Display payment page for a specific bill"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    customer_id = session["user_id"]
    
    # Get the bill and verify it belongs to the customer
    bill = db.session.query(Bill, User).join(User).filter(
        Bill.id == bill_id,
        Bill.customer_id == customer_id,
        Bill.is_paid == False
    ).first()
    
    if not bill:
        flash("Bill not found or already paid", "error")
        return redirect(url_for("customer_dashboard"))
    
    bill_obj, user = bill
    
    return render_template("payment.html", 
                         bill=bill_obj, 
                         user=user,
                         stripe_publishable_key=app.config["STRIPE_PUBLISHABLE_KEY"])


@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    """Create Stripe Payment Intent for bill payment"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        bill_id = data.get("bill_id")
        
        if not bill_id:
            return jsonify({"error": "Bill ID required"}), 400
        
        customer_id = session["user_id"]
        
        # Get the bill and verify it belongs to the customer
        bill = Bill.query.filter_by(
            id=bill_id, 
            customer_id=customer_id, 
            is_paid=False
        ).first()
        
        if not bill:
            return jsonify({"error": "Bill not found or already paid"}), 404
        
        # Create Stripe Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=bill.amount * 100,  # Convert rupees to paise
            currency="inr",
            metadata={
                "bill_id": bill_id,
                "customer_id": customer_id,
                "month": bill.month,
                "year": bill.year
            },
            description=f"TiffinTrack Bill - {bill.month}/{bill.year}"
        )
        
        # Save payment record
        payment = Payment(
            bill_id=bill_id,
            customer_id=customer_id,
            stripe_payment_intent_id=intent.id,
            amount=bill.amount * 100,  # Store in paise
            status="pending"
        )
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        })
        
    except Exception as e:
        print(f"Error creating payment intent: {e}")
        return jsonify({"error": "Failed to create payment intent"}), 500


@app.route("/payment-success", methods=["POST", "GET"])
@db_retry(max_retries=3, delay=1)
def payment_success():
    """Handle successful payment confirmation with comprehensive updates"""
    
    # Handle GET request (redirect from payment page)
    if request.method == "GET":
        if "user_id" not in session:
            return redirect(url_for("login"))
        
        # Get payment details from query params or session
        payment_intent_id = request.args.get("payment_intent_id")
        
        if payment_intent_id:
            try:
                # Retrieve payment details
                payment = Payment.query.filter_by(
                    stripe_payment_intent_id=payment_intent_id
                ).first()
                
                if payment and payment.status == "succeeded":
                    bill = Bill.query.get(payment.bill_id)
                    
                    payment_details = {
                        "transaction_id": payment_intent_id,
                        "amount": payment.amount // 100,  # Convert from paise to rupees
                        "billing_period": f"{bill.month}/{bill.year}" if bill else "N/A",
                        "date": payment.updated_at.strftime("%d %b %Y, %I:%M %p") if payment.updated_at else datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        "payment_method": payment.payment_method or "card"
                    }
                    
                    return render_template("payment_success.html", payment_details=payment_details)
            except Exception as e:
                print(f"Error loading payment success page: {e}")
        
        # Fallback if no payment details
        return render_template("payment_success.html", payment_details=None)
    
    # Handle POST request (from payment form)
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        payment_intent_id = data.get("payment_intent_id")
        
        if not payment_intent_id:
            return jsonify({"error": "Payment Intent ID required"}), 400
        
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == "succeeded":
            # Process payment success with comprehensive updates
            result = process_payment_success(payment_intent_id, intent)
            
            if result["success"]:
                return jsonify({
                    "success": True,
                    "message": "Payment successful! Your bill has been paid.",
                    "bill_id": result["bill_id"],
                    "amount": result["amount"],
                    "payment_date": result["payment_date"],
                    "redirect_url": url_for("payment_success", payment_intent_id=payment_intent_id, _external=False)
                })
            else:
                return jsonify({"error": result["error"]}), 404
        else:
            return jsonify({"error": "Payment not completed"}), 400
            
    except Exception as e:
        print(f"Error processing payment success: {e}")
        return jsonify({"error": "Failed to process payment"}), 500


@app.route("/payment-failed")
def payment_failed():
    """Display payment failed page"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    error_message = request.args.get("error", "Payment could not be processed")
    bill_id = request.args.get("bill_id")
    
    return render_template("payment_failed.html", 
                         error_message=error_message,
                         bill_id=bill_id)


def process_payment_success(payment_intent_id, stripe_intent):
    """
    Comprehensive payment success processing that updates everything
    Returns: dict with success status and details
    """
    try:
        # Find payment record
        payment = Payment.query.filter_by(
            stripe_payment_intent_id=payment_intent_id
        ).first()
        
        if not payment:
            return {"success": False, "error": "Payment record not found"}
        
        # Get bill and customer info
        bill = Bill.query.get(payment.bill_id)
        customer = User.query.get(payment.customer_id)
        
        if not bill or not customer:
            return {"success": False, "error": "Bill or customer not found"}
        
        # Update payment record with detailed information
        payment.status = "succeeded"
        payment.payment_method = (
            stripe_intent.charges.data[0].payment_method_details.type 
            if stripe_intent.charges.data else "unknown"
        )
        payment.updated_at = datetime.now()
        
        # Mark bill as paid
        bill.is_paid = True
        
        # Create payment success log entry
        payment_log = {
            "timestamp": datetime.now().isoformat(),
            "payment_id": payment.id,
            "bill_id": bill.id,
            "customer_id": customer.id,
            "customer_name": customer.fullname,
            "customer_email": customer.email,
            "amount": bill.amount,
            "currency": payment.currency,
            "payment_method": payment.payment_method,
            "stripe_payment_intent_id": payment_intent_id,
            "billing_period": f"{bill.month}/{bill.year}",
            "billable_days": bill.billable_days,
            "paused_days": bill.paused_days
        }
        
        # Commit to current database (SQLite or PostgreSQL)
        db.session.commit()
        
        # Sync to Neon database if currently using SQLite
        sync_payment_to_neon(payment_log)
        
        # Log successful payment
        print(f"💰 Payment Success: {customer.fullname} paid ₹{bill.amount} for {bill.month}/{bill.year}")
        
        # Update analytics and metrics
        update_payment_analytics(payment_log)
        
        return {
            "success": True,
            "bill_id": bill.id,
            "amount": bill.amount,
            "payment_date": payment.updated_at.isoformat(),
            "customer_name": customer.fullname,
            "billing_period": f"{bill.month}/{bill.year}"
        }
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in process_payment_success: {e}")
        return {"success": False, "error": str(e)}


def sync_payment_to_neon(payment_log):
    """
    Sync payment data to Neon PostgreSQL database
    This ensures data consistency across databases
    """
    try:
        # Check if we're currently using SQLite
        current_db_url = app.config["SQLALCHEMY_DATABASE_URI"]
        
        if "sqlite" in current_db_url:
            print("🔄 Syncing payment to Neon database...")
            
            # Get original Neon URL from environment
            neon_url = os.getenv("DATABASE_URL")
            if not neon_url or "postgresql" not in neon_url:
                print("⚠️ No Neon URL available for sync")
                return
            
            # Try to sync to Neon
            try:
                import psycopg2
                import psycopg2.extras
                
                # Connect to Neon with shorter timeout
                conn = psycopg2.connect(neon_url, connect_timeout=10)
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                # Update payment record in Neon
                cursor.execute("""
                    UPDATE payments 
                    SET status = %s, payment_method = %s, updated_at = %s
                    WHERE stripe_payment_intent_id = %s
                """, (
                    'succeeded',
                    payment_log['payment_method'],
                    payment_log['timestamp'],
                    payment_log['stripe_payment_intent_id']
                ))
                
                # Update bill record in Neon
                cursor.execute("""
                    UPDATE bills 
                    SET is_paid = true
                    WHERE id = %s
                """, (payment_log['bill_id'],))
                
                # Insert payment log for audit trail
                cursor.execute("""
                    INSERT INTO payment_logs (
                        payment_id, bill_id, customer_id, amount, 
                        payment_method, stripe_payment_intent_id, 
                        billing_period, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stripe_payment_intent_id) DO NOTHING
                """, (
                    payment_log['payment_id'],
                    payment_log['bill_id'],
                    payment_log['customer_id'],
                    payment_log['amount'],
                    payment_log['payment_method'],
                    payment_log['stripe_payment_intent_id'],
                    payment_log['billing_period'],
                    payment_log['timestamp']
                ))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                print("✅ Payment synced to Neon database successfully")
                
            except Exception as neon_error:
                print(f"⚠️ Neon sync failed (continuing with local): {neon_error}")
                # Don't fail the payment if Neon sync fails
                pass
        else:
            print("ℹ️ Already using PostgreSQL, no sync needed")
            
    except Exception as e:
        print(f"⚠️ Error in sync_payment_to_neon: {e}")
        # Don't fail the payment process if sync fails


def update_payment_analytics(payment_log):
    """Update payment analytics and metrics"""
    try:
        # Log payment metrics
        print(f"📊 Payment Analytics Updated:")
        print(f"   Customer: {payment_log['customer_name']}")
        print(f"   Amount: ₹{payment_log['amount']}")
        print(f"   Period: {payment_log['billing_period']}")
        print(f"   Method: {payment_log['payment_method']}")
        print(f"   Days: {payment_log['billable_days']} billable, {payment_log['paused_days']} paused")
        
        # Here you could add more analytics like:
        # - Update monthly revenue totals
        # - Track payment method preferences
        # - Calculate customer lifetime value
        # - Update collection efficiency metrics
        
    except Exception as e:
        print(f"⚠️ Error updating analytics: {e}")


@app.route("/payment-webhook", methods=["POST"])
@db_retry(max_retries=3, delay=1)
def payment_webhook():
    """Handle Stripe webhooks for payment status updates with comprehensive processing"""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        # Verify webhook signature
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            # For development, parse without verification
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        
        print(f"🔔 Webhook received: {event['type']}")
        
        # Handle payment intent events
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            
            # Process payment success through comprehensive handler
            result = process_payment_success(payment_intent["id"], payment_intent)
            
            if result["success"]:
                print(f"✅ Webhook processed payment success for bill {result['bill_id']}")
            else:
                print(f"❌ Webhook failed to process payment: {result['error']}")
                
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            
            # Update payment status to failed
            payment = Payment.query.filter_by(
                stripe_payment_intent_id=payment_intent["id"]
            ).first()
            
            if payment:
                payment.status = "failed"
                payment.updated_at = datetime.now()
                db.session.commit()
                
                # Log failed payment
                customer = User.query.get(payment.customer_id)
                bill = Bill.query.get(payment.bill_id)
                print(f"❌ Payment Failed: {customer.fullname if customer else 'Unknown'} - ₹{bill.amount if bill else 'Unknown'}")
                
                # Sync failure to Neon if needed
                if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
                    try:
                        neon_url = os.getenv("DATABASE_URL")
                        if neon_url and "postgresql" in neon_url:
                            import psycopg2
                            conn = psycopg2.connect(neon_url, connect_timeout=5)
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE payments 
                                SET status = 'failed', updated_at = %s
                                WHERE stripe_payment_intent_id = %s
                            """, (datetime.now(), payment_intent["id"]))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            print("✅ Payment failure synced to Neon")
                    except:
                        print("⚠️ Failed to sync payment failure to Neon")
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": "Webhook processing failed"}), 400

# ------------------------
# CLI Commands for Database Management
# ------------------------

@app.cli.command()
def seed_db():
    """Seed the database with initial data"""
    seed_initial_data()
    print("🌱 Database seeded successfully!")

@app.cli.command()
def reset_db():
    """Reset database - drop all tables and recreate"""
    db.drop_all()
    db.create_all()
    seed_initial_data()
    print("🔄 Database reset complete!")

# ------------------------
# Application Entry Point
# ------------------------

if __name__ == "__main__":
    print("🚀 Starting TiffinTrack server...")
    
    # Verify database connection before starting
    if not verify_database_connection():
        print("❌ Cannot establish database connection. Exiting.")
        exit(1)
    
    if "mysql" in DATABASE_URL:
        print("🔗 Connected to MySQL database")
    elif "postgresql" in DATABASE_URL:
        print("🔗 Connected to Neon PostgreSQL database")
    else:
        print("🔗 Using SQLite database for development")
    app.run(debug=True, host='127.0.0.1', port=5000)
