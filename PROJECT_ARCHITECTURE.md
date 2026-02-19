# TiffinTrack - Project Architecture & Database Structure

## Project Overview
TiffinTrack is a comprehensive tiffin (meal) delivery management system for Navi Mumbai. It handles meal plan subscriptions, delivery scheduling, billing, payments, and customer management.

---

## Major Modules

### 1. Authentication & User Management
**Purpose**: Handle user registration, login, profile management

**Routes**:
- `GET/POST /register` - User registration with address validation
- `GET/POST /login` - User authentication
- `GET/POST /profile` - Profile management with address lock during active plans
- `GET /logout` - Session termination

**Features**:
- Role-based access (Admin/Customer)
- Navi Mumbai area validation (16 areas)
- Address change restriction during active plans
- Password hashing with werkzeug
- Session management

**Templates**:
- `register_professional.html`
- `login_professional.html`
- `profile.html`

---

### 2. Plan Management (Customer)
**Purpose**: Multi-step meal plan selection and subscription

**Routes**:
- `GET /plans` - Step 1: Select meal plans
- `GET /plans/customize` - Step 2: Customize duration
- `GET /plans/checkout` - Step 3: Payment checkout
- `POST /plans/process-payment` - Create payment intent
- `POST /plans/payment-success` - Handle successful payment
- `POST /plans/save` - Legacy direct save

**Features**:
- 3-step selection flow (Select → Customize → Payment)
- Duration presets: 1, 3, 7, 30 days or custom dates
- Multiple plan selection
- Real-time cost calculation
- Stripe payment integration
- SessionStorage for data persistence
- Progress indicators

**Templates**:
- `choose_plans.html` - Plan selection
- `customize_plans.html` - Duration customization
- `plan_checkout.html` - Payment page

---

### 3. Admin Plan Management
**Purpose**: CRUD operations for meal plans

**Routes**:
- `GET /admin/plans` - List all plans
- `GET/POST /admin/plans/add` - Create new plan
- `GET/POST /admin/plans/edit/<id>` - Edit existing plan
- `POST /admin/plans/delete/<id>` - Delete plan
- `POST /admin/plans/toggle/<id>` - Toggle active status

**Features**:
- Plan creation with image upload
- Menu items as JSON
- Daily rate configuration
- Active/inactive status toggle
- Image management (upload, resize, optimize)

**Templates**:
- `admin_plans.html`
- `admin_plan_form.html`

---

### 4. Pause Management
**Purpose**: Allow customers to pause meal deliveries

**Routes**:
- `GET /pause` - Pause calendar page
- `POST /pause/save` - Add paused date
- `POST /pause/remove` - Remove paused date

**Features**:
- 8:00 AM cutoff time validation
- Visual calendar display
- Paused date cards with remove functionality
- Automatic billing adjustment
- Past date prevention

**Templates**:
- `pause_calendar.html`

---

### 5. Billing & Payments
**Purpose**: Generate bills, process payments, track payment history

**Routes**:
- `GET /billing` - Customer billing page
- `GET /bills` - Admin bill management
- `GET /bills/generate/<month>/<year>` - Generate monthly bills
- `GET /bills/mark-paid/<id>` - Mark bill as paid (admin)
- `GET /payment/<bill_id>` - Payment page
- `POST /create-payment-intent` - Create Stripe payment intent
- `POST /payment-success` - Handle payment success
- `GET /payment-failed` - Payment failure page
- `POST /payment-webhook` - Stripe webhook handler

**Features**:
- Automatic monthly bill generation
- Paused days deduction
- Stripe payment integration
- Payment history tracking
- Unpaid/paid bill separation
- Transaction logging
- Dual database sync (SQLite + PostgreSQL)

**Templates**:
- `billing.html` - Customer billing
- `bill_management_professional.html` - Admin billing
- `payment.html` - Payment form
- `payment_success.html` - Success page
- `payment_failed.html` - Failure page

---

### 6. Customer Management (Admin)
**Purpose**: Manage customer accounts and subscriptions

**Routes**:
- `GET /customers` - Customer list with search
- `POST /customers/add` - Add new customer

**Features**:
- Customer search and filtering
- Active plan tracking
- Unpaid bill monitoring
- Customer statistics
- Quick add functionality

**Templates**:
- `customer_management.html`

---

### 7. Kitchen Report (Admin)
**Purpose**: Daily meal preparation planning

**Routes**:
- `GET /kitchen-report` - Kitchen preparation report

**Features**:
- Date-based meal count
- Plan-wise breakdown
- Paused meal exclusion
- Area-wise distribution
- Printable format

**Templates**:
- `kitchen_report_professional.html`

---

### 8. Delivery Routes (Admin)
**Purpose**: Optimize delivery logistics

**Routes**:
- `GET /delivery-routes` - Delivery route planning

**Features**:
- Area-wise customer grouping
- Active plan filtering
- Paused delivery exclusion
- Address display
- Route optimization suggestions

**Templates**:
- `delivery_routes_professional.html`

---

### 9. Analytics Dashboard (Admin)
**Purpose**: Business intelligence and reporting

**Routes**:
- `GET /analytics` - Analytics dashboard

**Features**:
- Revenue tracking
- Customer growth metrics
- Plan popularity analysis
- Payment collection efficiency
- Monthly trends
- Area-wise distribution
- Visual charts and graphs

**Templates**:
- `analytics_professional.html`

---

### 10. Dashboards
**Purpose**: Main navigation hubs

**Routes**:
- `GET /` - Landing page
- `GET /dashboard` - Customer dashboard
- `GET /admin` - Admin dashboard

**Features**:
- Role-based dashboard
- Quick stats overview
- Recent activity
- Action shortcuts
- Navigation menu

**Templates**:
- `index_professional.html` - Landing
- `customer_dashboard_professional.html` - Customer
- `admin_dashboard_professional.html` - Admin

---

## Database Structure

### Entity Relationship Diagram

```
┌─────────────┐
│    User     │
│  (users)    │
└──────┬──────┘
       │
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  ▼
┌─────────────────┐              ┌──────────────┐
│  CustomerPlan   │              │ PausedDate   │
│(customer_plans) │              │(paused_dates)│
└────────┬────────┘              └──────────────┘
         │
         │ ┌──────────┐
         └─┤   Plan   │
           │ (plans)  │
           └──────────┘
       
       ┌──────────┐
       │   Bill   │
       │ (bills)  │
       └────┬─────┘
            │
            ▼
       ┌──────────┐
       │ Payment  │
       │(payments)│
       └────┬─────┘
            │
            ▼
     ┌─────────────┐
     │ PaymentLog  │
     │(payment_logs)│
     └─────────────┘

       ┌──────────┐
       │   Menu   │
       │ (menus)  │
       └──────────┘
```

---

## Database Tables

### 1. users
**Purpose**: Store user accounts (customers and admins)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique user ID |
| fullname | String(100) | NOT NULL | Full name |
| email | String(120) | UNIQUE, NOT NULL | Email address |
| phone | String(20) | NOT NULL | Phone number |
| password | String(255) | NOT NULL | Hashed password |
| addr1 | String(255) | NOT NULL | Address line 1 |
| addr2 | String(255) | NULL | Address line 2 |
| area | String(100) | NOT NULL | Navi Mumbai area |
| city | String(100) | NOT NULL, DEFAULT='Navi Mumbai' | City |
| state | String(100) | NOT NULL, DEFAULT='Maharashtra' | State |
| pincode | String(10) | NOT NULL | Postal code |
| is_admin | Boolean | DEFAULT=False | Admin flag |
| created_at | DateTime | DEFAULT=NOW() | Registration date |

**Relationships**:
- One-to-Many with CustomerPlan
- One-to-Many with PausedDate
- One-to-Many with Bill
- One-to-Many with Payment
- One-to-Many with PaymentLog

**Indexes**:
- UNIQUE on email
- INDEX on area (for delivery routing)

---

### 2. plans
**Purpose**: Store meal plan templates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique plan ID |
| name | String(100) | NOT NULL | Plan name (e.g., "Veg Thali") |
| daily_rate | Integer | NOT NULL | Price per day in rupees |
| description | String(255) | NULL | Plan description |
| items | Text | NULL | JSON string of menu items |
| image_filename | String(255) | NULL | Image file name |
| is_active | Boolean | DEFAULT=True | Active status |
| created_at | DateTime | DEFAULT=NOW() | Creation date |

**Relationships**:
- One-to-Many with CustomerPlan
- One-to-Many with Menu

**Sample items JSON**:
```json
["Basmati Rice", "Dal Tadka", "Mixed Vegetable Curry", "2 Rotis", "Fresh Salad", "Pickle"]
```

---

### 3. customer_plans
**Purpose**: Track customer meal plan subscriptions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique subscription ID |
| customer_id | Integer | FOREIGN KEY(users.id), NOT NULL | Customer reference |
| plan_id | Integer | FOREIGN KEY(plans.id), NOT NULL | Plan reference |
| start_date | Date | NOT NULL | Subscription start |
| end_date | Date | NOT NULL | Subscription end |
| is_active | Boolean | DEFAULT=True | Active status |
| created_at | DateTime | DEFAULT=NOW() | Creation date |

**Relationships**:
- Many-to-One with User
- Many-to-One with Plan

**Business Rules**:
- Address cannot be changed while active plans exist
- Used for delivery scheduling
- Affects billing calculations

---

### 4. paused_dates
**Purpose**: Track dates when customer paused delivery

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique pause ID |
| customer_id | Integer | FOREIGN KEY(users.id), NOT NULL | Customer reference |
| pause_date | Date | NOT NULL | Paused date |
| created_at | DateTime | DEFAULT=NOW() | Creation date |

**Relationships**:
- Many-to-One with User

**Business Rules**:
- Cannot pause after 8:00 AM on delivery date
- Cannot pause past dates
- Automatically deducted from billing
- Affects kitchen report counts

---

### 5. bills
**Purpose**: Store monthly billing records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique bill ID |
| customer_id | Integer | FOREIGN KEY(users.id), NOT NULL | Customer reference |
| month | Integer | NOT NULL | Month (1-12) |
| year | Integer | NOT NULL | Year |
| total_days | Integer | NOT NULL | Total days in period |
| paused_days | Integer | NOT NULL | Days paused |
| billable_days | Integer | NOT NULL | Days to charge |
| amount | Integer | NOT NULL | Total amount in rupees |
| is_paid | Boolean | DEFAULT=False | Payment status |
| created_at | DateTime | DEFAULT=NOW() | Generation date |

**Relationships**:
- Many-to-One with User
- One-to-Many with Payment
- One-to-Many with PaymentLog

**Calculation**:
```
billable_days = total_days - paused_days
amount = billable_days × daily_rate
```

---

### 6. payments
**Purpose**: Track Stripe payment transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique payment ID |
| bill_id | Integer | FOREIGN KEY(bills.id), NOT NULL | Bill reference |
| customer_id | Integer | FOREIGN KEY(users.id), NOT NULL | Customer reference |
| stripe_payment_intent_id | String(255) | UNIQUE, NOT NULL | Stripe intent ID |
| amount | Integer | NOT NULL | Amount in paise (₹1 = 100 paise) |
| currency | String(3) | DEFAULT='inr', NOT NULL | Currency code |
| status | String(50) | NOT NULL | Payment status |
| payment_method | String(50) | NULL | Payment method type |
| created_at | DateTime | DEFAULT=NOW() | Creation date |
| updated_at | DateTime | DEFAULT=NOW(), ON UPDATE=NOW() | Last update |

**Relationships**:
- Many-to-One with Bill
- Many-to-One with User
- One-to-Many with PaymentLog

**Status Values**:
- `pending` - Payment initiated
- `succeeded` - Payment successful
- `failed` - Payment failed

---

### 7. payment_logs
**Purpose**: Audit trail for payment transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique log ID |
| payment_id | Integer | FOREIGN KEY(payments.id), NOT NULL | Payment reference |
| bill_id | Integer | FOREIGN KEY(bills.id), NOT NULL | Bill reference |
| customer_id | Integer | FOREIGN KEY(users.id), NOT NULL | Customer reference |
| amount | Integer | NOT NULL | Amount in paise |
| payment_method | String(50) | NULL | Payment method |
| stripe_payment_intent_id | String(255) | UNIQUE, NOT NULL | Stripe intent ID |
| billing_period | String(20) | NULL | Period (MM/YYYY) |
| status | String(50) | DEFAULT='completed' | Log status |
| created_at | DateTime | DEFAULT=NOW() | Log date |

**Relationships**:
- Many-to-One with Payment
- Many-to-One with Bill
- Many-to-One with User

**Purpose**:
- Audit trail
- Transaction history
- Reconciliation
- Reporting

---

### 8. menus
**Purpose**: Store daily menu items (future feature)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique menu ID |
| date | Date | NOT NULL | Menu date |
| plan_id | Integer | FOREIGN KEY(plans.id), NOT NULL | Plan reference |
| items | Text | NOT NULL | JSON string of items |
| created_at | DateTime | DEFAULT=NOW() | Creation date |

**Relationships**:
- Many-to-One with Plan

**Status**: Currently not actively used, prepared for future menu planning feature

---

## Configuration Constants

### Navi Mumbai Areas (16 areas)
```python
NAVI_MUMBAI_AREAS = [
    "Vashi", "Nerul", "Belapur", "Kharghar", "Panvel", "Kamothe",
    "Ghansoli", "Kopar Khairane", "Airoli", "Sanpada", "Juinagar",
    "Seawoods", "Darave", "Digha", "Karave", "Ulwe"
]
```

### Business Rules
- **Cutoff Time**: 8:00 AM for pause/unpause
- **Currency**: INR (Indian Rupees)
- **Payment Storage**: Paise (₹1 = 100 paise)
- **Service Area**: Navi Mumbai only
- **Billing Cycle**: Monthly

---

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL (Neon) with SQLite fallback
- **Migrations**: Flask-Migrate (Alembic)
- **Authentication**: Session-based with werkzeug password hashing
- **Payment**: Stripe API

### Frontend
- **Template Engine**: Jinja2
- **CSS**: Custom CSS with CSS variables
- **JavaScript**: Vanilla JS (no frameworks)
- **Icons**: Font Awesome 6.5.1
- **Storage**: SessionStorage for multi-step flows

### Infrastructure
- **Image Processing**: Pillow (PIL)
- **Environment**: python-dotenv
- **Email**: SMTP (configured but optional)
- **Deployment**: Neon PostgreSQL (cloud)

---

## Key Features

### Security
- Password hashing
- Session management
- CSRF protection (Flask built-in)
- SQL injection prevention (SQLAlchemy ORM)
- Address lock during active plans
- Admin role verification

### Performance
- Database connection pooling
- Retry logic for database operations
- Image optimization and resizing
- Efficient queries with proper indexes
- Fallback to SQLite on connection failure

### User Experience
- Multi-step flows with progress indicators
- Real-time validation
- Auto-hide flash messages
- Mobile-responsive design
- Visual feedback for all actions
- Smooth animations

### Business Logic
- Automatic billing calculation
- Paused day deduction
- Cutoff time enforcement
- Area-based delivery routing
- Payment reconciliation
- Dual database sync

---

## File Structure

```
TiffinTrack/
├── app.py                          # Main application file
├── start_app.py                    # Application starter
├── utils.py                        # Utility functions
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── migrations/                    # Database migrations
│   ├── versions/
│   └── alembic.ini
├── instance/
│   └── tiffintrack.db            # SQLite database (fallback)
├── static/
│   ├── css/
│   │   └── professional.css      # Main stylesheet
│   ├── images/                   # Static images
│   │   ├── logo.svg
│   │   └── favicon.svg
│   ├── favicon/                  # Favicon files
│   └── uploads/
│       └── dishes/               # Uploaded plan images
├── templates/                    # Jinja2 templates
│   ├── index_professional.html
│   ├── login_professional.html
│   ├── register_professional.html
│   ├── profile.html
│   ├── customer_dashboard_professional.html
│   ├── admin_dashboard_professional.html
│   ├── choose_plans.html
│   ├── customize_plans.html
│   ├── plan_checkout.html
│   ├── pause_calendar.html
│   ├── billing.html
│   ├── payment.html
│   ├── payment_success.html
│   ├── payment_failed.html
│   ├── customer_management.html
│   ├── admin_plans.html
│   ├── admin_plan_form.html
│   ├── kitchen_report_professional.html
│   ├── delivery_routes_professional.html
│   ├── bill_management_professional.html
│   ├── analytics_professional.html
│   └── terms.html
└── Documentation/
    ├── PLAN_FLOW_UPDATE.md
    ├── PROFILE_PAGE_UPDATE.md
    ├── ENDPOINT_AUDIT_REPORT.md
    ├── ENDPOINT_FIXES.md
    ├── PAYMENT_PAGES_UPDATE.md
    ├── DESIGN_UPDATES.md
    ├── LOGO_UPDATE.md
    └── PROJECT_ARCHITECTURE.md (this file)
```

---

## API Endpoints Summary

### Public Routes
- `GET /` - Landing page
- `GET/POST /login` - Authentication
- `GET/POST /register` - Registration
- `GET /terms` - Terms & conditions

### Customer Routes (Authenticated)
- `GET /dashboard` - Customer dashboard
- `GET/POST /profile` - Profile management
- `GET /plans` - Plan selection
- `GET /plans/customize` - Duration customization
- `GET /plans/checkout` - Payment checkout
- `GET /pause` - Pause calendar
- `POST /pause/save` - Add pause
- `POST /pause/remove` - Remove pause
- `GET /billing` - Billing page
- `GET /payment/<bill_id>` - Payment page
- `POST /create-payment-intent` - Create payment
- `POST /payment-success` - Payment success handler
- `GET /payment-failed` - Payment failure page

### Admin Routes (Admin Only)
- `GET /admin` - Admin dashboard
- `GET /admin/plans` - Plan management
- `GET/POST /admin/plans/add` - Add plan
- `GET/POST /admin/plans/edit/<id>` - Edit plan
- `POST /admin/plans/delete/<id>` - Delete plan
- `GET /customers` - Customer management
- `POST /customers/add` - Add customer
- `GET /kitchen-report` - Kitchen report
- `GET /delivery-routes` - Delivery routes
- `GET /bills` - Bill management
- `GET /bills/generate/<month>/<year>` - Generate bills
- `GET /bills/mark-paid/<id>` - Mark paid
- `GET /analytics` - Analytics dashboard

### Webhook Routes
- `POST /payment-webhook` - Stripe webhook
- `GET /health` - Health check

---

## Future Enhancements

1. **Menu Planning**: Daily menu customization per plan
2. **Notifications**: Email/SMS for delivery updates
3. **Ratings & Reviews**: Customer feedback system
4. **Referral Program**: Customer referral rewards
5. **Mobile App**: Native iOS/Android apps
6. **Multi-city**: Expand beyond Navi Mumbai
7. **Delivery Tracking**: Real-time GPS tracking
8. **Dietary Preferences**: Allergen filters, preferences
9. **Subscription Management**: Pause/resume subscriptions
10. **Advanced Analytics**: ML-based demand forecasting

---

## Maintenance Notes

### Database Migrations
```bash
# Create migration
flask db migrate -m "description"

# Apply migration
flask db upgrade

# Rollback
flask db downgrade
```

### Backup Strategy
- Daily automated backups of PostgreSQL
- SQLite fallback for development
- Payment logs for transaction recovery

### Monitoring
- Health check endpoint: `/health`
- Database connection retry logic
- Error logging to console
- Stripe webhook for payment verification

---

**Last Updated**: February 2026
**Version**: 2.0
**Maintainer**: TiffinTrack Team
