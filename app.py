import os
import json
from datetime import datetime, date, time, timedelta
from calendar import monthrange
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from PIL import Image

# ------------------------
# Environment Setup
# ------------------------
load_dotenv()

app = Flask(__name__)

# Database Configuration for MySQL/SQLite
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///tiffintrack.db"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "tiffintrack-secret-key-2026")

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

if "mysql" in DATABASE_URL:
    print(f"🔗 Connected to MySQL database")
elif "postgresql" in DATABASE_URL:
    print(f"🔗 Connected to Neon PostgreSQL database")
else:
    print(f"🔗 Using SQLite database for development")

# Template filters
@app.template_filter('strptime')
def strptime_filter(date_string, format='%Y-%m-%d'):
    """Parse date string to datetime object"""
    return datetime.strptime(date_string, format).date()

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
    description = db.Column(db.String(255))
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

        user = User(
            fullname=fullname,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            addr1=addr1,
            addr2=addr2,
            area=request.form.get("area", "Vashi"),  # Default to Vashi
            city="Navi Mumbai",  # Force Navi Mumbai
            state="Maharashtra",  # Force Maharashtra
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
    
    stats = {
        'total_customers': total_customers,
        'today_meals': today_meals,
        'today_paused': today_paused,
        'pending_bills': pending_bills
    }
    
    return render_template("admin_dashboard.html", stats=stats)

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
        active_plan = db.session.query(CustomerPlan, Plan).join(Plan).filter(
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
    active_plans = db.session.query(CustomerPlan, Plan, User).join(Plan).join(User).filter(
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
    
    for cp, plan, user in active_plans:
        if user.id not in paused_customer_ids:
            if plan.name not in production_data:
                production_data[plan.name] = {
                    'count': 0,
                    'items': json.loads(plan.items) if plan.items else []
                }
            production_data[plan.name]['count'] += 1
            total_meals += 1
    
    return render_template("kitchen_report.html", 
                         production_data=production_data, 
                         total_meals=total_meals,
                         report_date=today)


# ---------- Delivery Routes ----------
@app.route("/delivery-routes")
def delivery_routes():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    today = date.today()
    
    # Get all customers with active deliveries today (not paused)
    active_deliveries = db.session.query(User, CustomerPlan, Plan).join(CustomerPlan).join(Plan).filter(
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
    
    for user, cp, plan in active_deliveries:
        if user.id not in paused_customer_ids:
            area = user.area  # Fixed from delivery_area to area
            if area not in routes:
                routes[area] = []
            
            routes[area].append({
                'name': user.fullname,
                'phone': user.phone,
                'address': f"{user.addr1}, {user.addr2 or ''}, {user.city}".strip(', '),
                'plan': plan.name
            })
    
    return render_template("delivery_routes.html", routes=routes, delivery_date=today)


# ---------- Bill Management ----------
@app.route("/bills")
def bill_management():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    bills = db.session.query(Bill, User).join(User).all()
    return render_template("bill_management.html", bills=bills)


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
        
        active_plans = db.session.query(CustomerPlan, Plan).join(Plan).filter(
            CustomerPlan.customer_id == customer.id,
            CustomerPlan.is_active == True,
            CustomerPlan.start_date <= last_day,
            CustomerPlan.end_date >= first_day
        ).all()
        
        if not active_plans:
            continue
        
        # Calculate total amount
        total_amount = 0
        total_days = monthrange(year, month)[1]
        
        # Get paused days for this customer in this month
        paused_days = PausedDate.query.filter(
            PausedDate.customer_id == customer.id,
            PausedDate.pause_date >= first_day,
            PausedDate.pause_date <= last_day
        ).count()
        
        billable_days = total_days - paused_days
        
        # Calculate amount based on active plans
        for cp, plan in active_plans:
            # Calculate overlap days
            plan_start = max(cp.start_date, first_day)
            plan_end = min(cp.end_date, last_day)
            plan_days = (plan_end - plan_start).days + 1
            
            # Get paused days for this specific plan period
            plan_paused = PausedDate.query.filter(
                PausedDate.customer_id == customer.id,
                PausedDate.pause_date >= plan_start,
                PausedDate.pause_date <= plan_end
            ).count()
            
            plan_billable_days = plan_days - plan_paused
            total_amount += plan_billable_days * plan.daily_rate
        
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


@app.route("/dashboard")
def customer_dashboard():
    if "user_id" not in session or session.get("is_admin"):
        return redirect(url_for("login"))
    
    customer_id = session["user_id"]
    
    # Get customer's active plans
    active_plans = db.session.query(CustomerPlan, Plan).join(Plan).filter(
        CustomerPlan.customer_id == customer_id,
        CustomerPlan.is_active == True,
        CustomerPlan.end_date >= date.today()
    ).all()
    
    # Get current month's paused days
    current_month = date.today().month
    current_year = date.today().year
    paused_this_month = PausedDate.query.filter(
        PausedDate.customer_id == customer_id,
        db.extract('month', PausedDate.pause_date) == current_month,
        db.extract('year', PausedDate.pause_date) == current_year
    ).count()
    
    # Calculate estimated bill for current month
    estimated_bill = 0
    total_days = monthrange(current_year, current_month)[1]
    
    for cp, plan in active_plans:
        # Calculate overlap with current month
        plan_start = max(cp.start_date, date(current_year, current_month, 1))
        plan_end = min(cp.end_date, date(current_year, current_month, total_days))
        
        if plan_start <= plan_end:
            plan_days = (plan_end - plan_start).days + 1
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
    
    dashboard_data = {
        'active_plans': active_plans,
        'estimated_bill': estimated_bill,
        'paused_this_month': paused_this_month,
        'recent_pauses': recent_pauses,
        'paused_today': paused_today,
        'total_days': total_days
    }
    
    return render_template("customer_dashboard.html", **dashboard_data)


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
            
            if start_date < date.today():
                flash("Start date cannot be in the past", "error")
                return redirect(url_for("choose_plans"))
            
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
                'total_cost': plan_cost
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
        flash(f"Successfully subscribed to {plan['plan_name']} for {plan['duration_days']} days (₹{plan['total_cost']})", "success")
    else:
        flash(f"Successfully subscribed to {len(selected_plans)} plans. Total cost: ₹{total_cost}", "success")
    
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
    if "mysql" in DATABASE_URL:
        print("🔗 Connected to MySQL database")
    elif "postgresql" in DATABASE_URL:
        print("🔗 Connected to Neon PostgreSQL database")
    else:
        print("🔗 Using SQLite database for development")
    app.run(debug=True, host='127.0.0.1', port=5000)
