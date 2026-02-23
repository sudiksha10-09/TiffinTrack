# Chapter 5: System Design - Database Documentation

## 5.1 Basic Modules

### Module 1: User Management
**Purpose**: Manages user registration, login, and authentication for customers and administrators. Allows users to manage personal and delivery profile details. Implements role-based access control (Customer and Admin). Ensures secure session handling and controlled access to system features.

### Module 2: Meal Plan Management
**Purpose**: Allows administrators to create, update, activate, or deactivate meal plans. Stores details such as plan name, daily price, and included menu items. Displays available meal plans to customers for selection and subscription.

### Module 3: Subscription Management
**Purpose**: Enables customers to subscribe to one or more meal plans. Supports flexible subscription durations based on selected dates. Maintains active and inactive subscription records for billing and delivery scheduling.

### Module 4: Pause Management
**Purpose**: Allows customers to pause meal delivery on selected dates using a calendar-based interface. Enforces cutoff rules to prevent last-minute pauses. Automatically adjusts delivery schedules and billing based on paused days.

### Module 5: Billing and Payment Processing
**Purpose**: Generates monthly bills based on active subscriptions and paused days. Displays billing details to customers for review. Integrates secure online payment processing. Maintains payment status and transaction history.

### Module 6: Administrative Management
**Purpose**: Provides administrators with access to customer records and subscription details. Enables monitoring of billing, payments, and operational data. Generates kitchen preparation reports and delivery route information for efficient operations.

---

## 5.2 Data Design, Integrity and Constraints


### Module 1: User Management

#### Users Table

| Field | Type | Description |
|-------|------|-------------|
| id | INT (Primary Key, Auto Increment) | Unique ID for each user |
| fullname | VARCHAR(100), NOT NULL | User's full name |
| email | VARCHAR(120), UNIQUE, NOT NULL | User's email address (unique identifier) |
| phone | VARCHAR(20), NOT NULL | User's phone number |
| password | VARCHAR(255), NOT NULL | Hashed password for authentication |
| addr1 | VARCHAR(255), NOT NULL | Primary address line |
| addr2 | VARCHAR(255), NULL | Secondary address line (optional) |
| area | VARCHAR(100), NOT NULL | Delivery area in Navi Mumbai |
| city | VARCHAR(100), NOT NULL | City name (default: Navi Mumbai) |
| state | VARCHAR(100), NOT NULL | State name (default: Maharashtra) |
| pincode | VARCHAR(10), NOT NULL | Postal code |
| is_admin | BOOLEAN, DEFAULT FALSE | Role flag (TRUE for admin, FALSE for customer) |
| created_at | DATETIME, NOT NULL | Timestamp of user registration |

**Constraints:**
- PRIMARY KEY: id
- UNIQUE: email
- NOT NULL: fullname, email, phone, password, addr1, area, city, state, pincode
- CHECK: area IN (list of 16 Navi Mumbai areas)
- CHECK: is_admin IN (TRUE, FALSE)

**Indexes:**
- INDEX on email (for login queries)
- INDEX on area (for delivery route optimization)
- INDEX on is_admin (for role-based queries)

**Business Rules:**
- Email must be unique across all users
- Password must be hashed using werkzeug security
- Area must be one of the 16 approved Navi Mumbai areas
- Address cannot be changed while user has active meal plans
- Phone number must be exactly 10 digits
- Pincode must be exactly 6 digits



---

### Module 2: Meal Plan Management

#### Plans Table

| Field | Type | Description |
|-------|------|-------------|
| id | INT (Primary Key, Auto Increment) | Unique ID for each meal plan |
| name | VARCHAR(100), NOT NULL | Plan name (e.g., "Veg Thali") |
| daily_rate | INT, NOT NULL | Price per day in rupees |
| description | VARCHAR(255), NULL | Brief description of the plan |
| items | TEXT, NULL | JSON string of menu items included |
| image_filename | VARCHAR(255), NULL | Filename of plan image |
| is_active | BOOLEAN, DEFAULT TRUE | Active status of the plan |
| created_at | DATETIME, NOT NULL | Timestamp of plan creation |

**Constraints:**
- PRIMARY KEY: id
- NOT NULL: name, daily_rate
- CHECK: daily_rate > 0
- CHECK: is_active IN (TRUE, FALSE)

**Indexes:**
- INDEX on is_active (for filtering active plans)
- INDEX on name (for search functionality)

**Business Rules:**
- Plan name should be descriptive and unique
- Daily rate must be a positive integer
- Items stored as JSON array: ["Rice", "Dal", "Roti", "Salad"]
- Image must be uploaded to static/uploads/dishes/
- Only active plans are displayed to customers
- Inactive plans are hidden but not deleted (for historical records)

**Sample Items JSON:**
```json
["Basmati Rice", "Dal Tadka", "Mixed Vegetable Curry", "2 Rotis", "Fresh Salad", "Pickle"]
```



---

### Module 3: Subscription Management

#### Customer_Plans Table

| Field | Type | Description |
|-------|------|-------------|
| id | INT (Primary Key, Auto Increment) | Unique ID for each subscription |
| customer_id | INT, FOREIGN KEY (users.id), NOT NULL | Reference to customer |
| plan_id | INT, FOREIGN KEY (plans.id), NOT NULL | Reference to meal plan |
| start_date | DATE, NOT NULL | Subscription start date |
| end_date | DATE, NOT NULL | Subscription end date |
| is_active | BOOLEAN, DEFAULT TRUE | Active status of subscription |
| created_at | DATETIME, NOT NULL | Timestamp of subscription creation |

**Constraints:**
- PRIMARY KEY: id
- FOREIGN KEY: customer_id REFERENCES users(id) ON DELETE CASCADE
- FOREIGN KEY: plan_id REFERENCES plans(id) ON DELETE RESTRICT
- NOT NULL: customer_id, plan_id, start_date, end_date
- CHECK: end_date >= start_date
- CHECK: start_date >= CURRENT_DATE (for new subscriptions)
- CHECK: is_active IN (TRUE, FALSE)

**Indexes:**
- INDEX on customer_id (for customer queries)
- INDEX on plan_id (for plan popularity analysis)
- INDEX on is_active (for filtering active subscriptions)
- COMPOSITE INDEX on (customer_id, is_active) (for dashboard queries)
- INDEX on end_date (for expiry checks)

**Business Rules:**
- Customer can have multiple active subscriptions
- Start date cannot be in the past
- End date must be after or equal to start date
- Subscription duration calculated as: (end_date - start_date) + 1 days
- Active subscriptions prevent address changes
- Expired subscriptions (end_date < today) should be marked inactive
- Used for billing calculations and delivery scheduling



---

### Module 4: Pause Management

#### Paused_Dates Table

| Field | Type | Description |
|-------|------|-------------|
| id | INT (Primary Key, Auto Increment) | Unique ID for each paused date |
| customer_id | INT, FOREIGN KEY (users.id), NOT NULL | Reference to customer |
| pause_date | DATE, NOT NULL | Date when delivery is paused |
| created_at | DATETIME, NOT NULL | Timestamp when pause was created |

**Constraints:**
- PRIMARY KEY: id
- FOREIGN KEY: customer_id REFERENCES users(id) ON DELETE CASCADE
- NOT NULL: customer_id, pause_date
- UNIQUE: (customer_id, pause_date) - Prevent duplicate pauses
- CHECK: pause_date >= CURRENT_DATE (cannot pause past dates)

**Indexes:**
- INDEX on customer_id (for customer queries)
- INDEX on pause_date (for date-based queries)
- COMPOSITE INDEX on (customer_id, pause_date) (for duplicate checks)
- INDEX on created_at (for audit trail)

**Business Rules:**
- Cutoff time: 8:00 AM on the delivery date
- Cannot pause dates in the past
- Cannot pause same date twice
- Paused dates automatically deducted from monthly billing
- Affects kitchen report meal counts
- Affects delivery route planning
- Can be removed before cutoff time
- Used in billing calculation: billable_days = total_days - paused_days

**Validation Rules:**
- If pause_date == today AND current_time > 08:00:00, reject
- If pause_date < today, reject
- If pause already exists for (customer_id, pause_date), reject



---

### Module 5: Billing and Payment Processing

#### Bills Table

| Field | Type | Description |
|-------|------|-------------|
| id | INT (Primary Key, Auto Increment) | Unique ID for each bill |
| customer_id | INT, FOREIGN KEY (users.id), NOT NULL | Reference to customer |
| month | INT, NOT NULL | Billing month (1-12) |
| year | INT, NOT NULL | Billing year |
| total_days | INT, NOT NULL | Total days in billing period |
| paused_days | INT, NOT NULL | Number of days paused |
| billable_days | INT, NOT NULL | Days to charge (total - paused) |
| amount | INT, NOT NULL | Total amount in rupees |
| is_paid | BOOLEAN, DEFAULT FALSE | Payment status |
| created_at | DATETIME, NOT NULL | Bill generation timestamp |
| updated_at | DATETIME, NULL | Last update timestamp |

**Constraints:**
- PRIMARY KEY: id
- FOREIGN KEY: customer_id REFERENCES users(id) ON DELETE CASCADE
- NOT NULL: customer_id, month, year, total_days, paused_days, billable_days, amount
- CHECK: month BETWEEN 1 AND 12
- CHECK: year >= 2024
- CHECK: total_days > 0
- CHECK: paused_days >= 0
- CHECK: billable_days >= 0
- CHECK: billable_days = total_days - paused_days
- CHECK: amount >= 0
- CHECK: is_paid IN (TRUE, FALSE)
- UNIQUE: (customer_id, month, year) - One bill per customer per month

**Indexes:**
- INDEX on customer_id (for customer queries)
- INDEX on is_paid (for filtering unpaid bills)
- COMPOSITE INDEX on (customer_id, is_paid) (for dashboard)
- COMPOSITE INDEX on (month, year) (for monthly reports)
- INDEX on created_at (for chronological sorting)

**Business Rules:**
- One bill generated per customer per month
- Amount calculation: billable_days × daily_rate
- Paused days automatically deducted
- Bill marked as paid when payment succeeds
- Unpaid bills displayed prominently to customers
- Used for revenue tracking and analytics

**Calculation Formula:**
```
billable_days = total_days - paused_days
amount = billable_days × plan_daily_rate
```



#### Payments Table

| Field | Type | Description |
|-------|------|-------------|
| id | INT (Primary Key, Auto Increment) | Unique ID for each payment |
| bill_id | INT, FOREIGN KEY (bills.id), NOT NULL | Reference to bill |
| customer_id | INT, FOREIGN KEY (users.id), NOT NULL | Reference to customer |
| stripe_payment_intent_id | VARCHAR(255), UNIQUE, NOT NULL | Stripe payment intent ID |
| amount | INT, NOT NULL | Amount in paise (₹1 = 100 paise) |
| currency | VARCHAR(3), DEFAULT 'inr', NOT NULL | Currency code |
| status | VARCHAR(50), NOT NULL | Payment status |
| payment_method | VARCHAR(50), NULL | Payment method type |
| created_at | DATETIME, NOT NULL | Payment initiation timestamp |
| updated_at | DATETIME, NULL | Last update timestamp |

**Constraints:**
- PRIMARY KEY: id
- FOREIGN KEY: bill_id REFERENCES bills(id) ON DELETE RESTRICT
- FOREIGN KEY: customer_id REFERENCES users(id) ON DELETE CASCADE
- UNIQUE: stripe_payment_intent_id
- NOT NULL: bill_id, customer_id, stripe_payment_intent_id, amount, currency, status
- CHECK: amount > 0
- CHECK: currency = 'inr'
- CHECK: status IN ('pending', 'succeeded', 'failed')

**Indexes:**
- INDEX on bill_id (for bill queries)
- INDEX on customer_id (for customer payment history)
- INDEX on stripe_payment_intent_id (for Stripe webhook lookups)
- INDEX on status (for filtering by status)
- INDEX on created_at (for chronological sorting)

**Business Rules:**
- Amount stored in paise (multiply rupees by 100)
- Status values: 'pending', 'succeeded', 'failed'
- Payment method: 'card', 'upi', 'netbanking', etc.
- Stripe payment intent ID must be unique
- When status = 'succeeded', mark bill as paid
- Used for transaction tracking and reconciliation

**Status Flow:**
```
pending → succeeded (payment successful)
pending → failed (payment failed)
```



#### Payment_Logs Table

| Field | Type | Description |
|-------|------|-------------|
| id | INT (Primary Key, Auto Increment) | Unique ID for each log entry |
| payment_id | INT, FOREIGN KEY (payments.id), NOT NULL | Reference to payment |
| bill_id | INT, FOREIGN KEY (bills.id), NOT NULL | Reference to bill |
| customer_id | INT, FOREIGN KEY (users.id), NOT NULL | Reference to customer |
| amount | INT, NOT NULL | Amount in paise |
| payment_method | VARCHAR(50), NULL | Payment method used |
| stripe_payment_intent_id | VARCHAR(255), UNIQUE, NOT NULL | Stripe intent ID |
| billing_period | VARCHAR(20), NULL | Period in MM/YYYY format |
| status | VARCHAR(50), DEFAULT 'completed' | Log status |
| created_at | DATETIME, NOT NULL | Log creation timestamp |

**Constraints:**
- PRIMARY KEY: id
- FOREIGN KEY: payment_id REFERENCES payments(id) ON DELETE CASCADE
- FOREIGN KEY: bill_id REFERENCES bills(id) ON DELETE CASCADE
- FOREIGN KEY: customer_id REFERENCES users(id) ON DELETE CASCADE
- UNIQUE: stripe_payment_intent_id
- NOT NULL: payment_id, bill_id, customer_id, amount, stripe_payment_intent_id

**Indexes:**
- INDEX on payment_id (for payment queries)
- INDEX on bill_id (for bill queries)
- INDEX on customer_id (for customer audit trail)
- INDEX on created_at (for chronological sorting)
- INDEX on billing_period (for period-based reports)

**Business Rules:**
- Immutable audit trail of all payment transactions
- Created when payment succeeds
- Used for reconciliation and reporting
- Billing period format: "MM/YYYY" (e.g., "02/2026")
- Never deleted, only archived
- Used for financial audits and compliance



---

### Module 6: Administrative Management

#### Menus Table (Future Feature)

| Field | Type | Description |
|-------|------|-------------|
| id | INT (Primary Key, Auto Increment) | Unique ID for each menu |
| date | DATE, NOT NULL | Menu date |
| plan_id | INT, FOREIGN KEY (plans.id), NOT NULL | Reference to meal plan |
| items | TEXT, NOT NULL | JSON string of menu items |
| created_at | DATETIME, NOT NULL | Menu creation timestamp |

**Constraints:**
- PRIMARY KEY: id
- FOREIGN KEY: plan_id REFERENCES plans(id) ON DELETE CASCADE
- NOT NULL: date, plan_id, items
- UNIQUE: (date, plan_id) - One menu per plan per day

**Indexes:**
- INDEX on date (for date-based queries)
- INDEX on plan_id (for plan queries)
- COMPOSITE INDEX on (date, plan_id) (for menu lookups)

**Business Rules:**
- One menu per plan per day
- Items stored as JSON array
- Used for daily menu planning
- Currently not actively used (prepared for future)
- Will be used for menu customization feature

**Sample Items JSON:**
```json
{
  "breakfast": ["Poha", "Tea"],
  "lunch": ["Rice", "Dal", "Sabzi", "Roti"],
  "dinner": ["Chapati", "Paneer Curry", "Salad"]
}
```



---

## 5.3 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS TABLE                              │
│  (Customers & Administrators)                                    │
│  - id (PK)                                                       │
│  - fullname, email (UNIQUE), phone, password                    │
│  - addr1, addr2, area, city, state, pincode                     │
│  - is_admin (role flag)                                         │
│  - created_at                                                    │
└────────┬────────────────────────────────────┬──────────────────┘
         │                                    │
         │ 1:N                                │ 1:N
         │                                    │
         ▼                                    ▼
┌─────────────────────┐              ┌──────────────────┐
│  CUSTOMER_PLANS     │              │  PAUSED_DATES    │
│  - id (PK)          │              │  - id (PK)       │
│  - customer_id (FK) │              │  - customer_id   │
│  - plan_id (FK)     │              │  - pause_date    │
│  - start_date       │              │  - created_at    │
│  - end_date         │              └──────────────────┘
│  - is_active        │
│  - created_at       │
└──────┬──────────────┘
       │
       │ N:1
       │
       ▼
┌─────────────────────┐
│     PLANS TABLE     │
│  - id (PK)          │
│  - name             │
│  - daily_rate       │
│  - description      │
│  - items (JSON)     │
│  - image_filename   │
│  - is_active        │
│  - created_at       │
└─────────────────────┘


┌─────────────────────┐
│    BILLS TABLE      │
│  - id (PK)          │
│  - customer_id (FK) │
│  - month, year      │
│  - total_days       │
│  - paused_days      │
│  - billable_days    │
│  - amount           │
│  - is_paid          │
│  - created_at       │
└──────┬──────────────┘
       │
       │ 1:N
       │
       ▼
┌─────────────────────┐
│   PAYMENTS TABLE    │
│  - id (PK)          │
│  - bill_id (FK)     │
│  - customer_id (FK) │
│  - stripe_intent_id │
│  - amount (paise)   │
│  - currency         │
│  - status           │
│  - payment_method   │
│  - created_at       │
│  - updated_at       │
└──────┬──────────────┘
       │
       │ 1:N
       │
       ▼
┌─────────────────────┐
│  PAYMENT_LOGS       │
│  - id (PK)          │
│  - payment_id (FK)  │
│  - bill_id (FK)     │
│  - customer_id (FK) │
│  - amount           │
│  - payment_method   │
│  - stripe_intent_id │
│  - billing_period   │
│  - status           │
│  - created_at       │
└─────────────────────┘


┌─────────────────────┐
│    MENUS TABLE      │
│  (Future Feature)   │
│  - id (PK)          │
│  - date             │
│  - plan_id (FK)     │
│  - items (JSON)     │
│  - created_at       │
└─────────────────────┘
```



---

## 5.4 Relationships and Cardinality

### One-to-Many Relationships

1. **Users → Customer_Plans** (1:N)
   - One user can have multiple meal plan subscriptions
   - CASCADE DELETE: When user deleted, all subscriptions deleted

2. **Users → Paused_Dates** (1:N)
   - One user can pause multiple dates
   - CASCADE DELETE: When user deleted, all paused dates deleted

3. **Users → Bills** (1:N)
   - One user can have multiple bills
   - CASCADE DELETE: When user deleted, all bills deleted

4. **Users → Payments** (1:N)
   - One user can make multiple payments
   - CASCADE DELETE: When user deleted, all payments deleted

5. **Plans → Customer_Plans** (1:N)
   - One plan can be subscribed by multiple customers
   - RESTRICT DELETE: Cannot delete plan if active subscriptions exist

6. **Bills → Payments** (1:N)
   - One bill can have multiple payment attempts
   - RESTRICT DELETE: Cannot delete bill if payments exist

7. **Payments → Payment_Logs** (1:N)
   - One payment can have multiple log entries
   - CASCADE DELETE: When payment deleted, logs deleted

8. **Plans → Menus** (1:N)
   - One plan can have multiple daily menus
   - CASCADE DELETE: When plan deleted, menus deleted



---

## 5.5 Data Integrity Rules

### Referential Integrity
- All foreign keys must reference existing primary keys
- CASCADE DELETE for dependent records (user data)
- RESTRICT DELETE for referenced records (plans with subscriptions)
- ON UPDATE CASCADE for primary key changes

### Domain Integrity
- Data types strictly enforced
- NOT NULL constraints on required fields
- CHECK constraints for valid value ranges
- DEFAULT values for optional fields

### Entity Integrity
- Primary keys are unique and not null
- Auto-increment for surrogate keys
- Composite unique constraints where needed

### Business Rule Integrity
- Cutoff time enforcement (8:00 AM)
- Date validation (no past dates for new records)
- Amount calculations (billable_days = total - paused)
- Status transitions (pending → succeeded/failed)
- Role-based access control



---

## 5.6 Database Normalization

### Current Normalization Level: 3NF (Third Normal Form)

#### 1NF (First Normal Form) ✅
- All tables have primary keys
- All columns contain atomic values
- No repeating groups
- Each column contains only one value

#### 2NF (Second Normal Form) ✅
- Meets 1NF requirements
- No partial dependencies
- All non-key attributes fully dependent on primary key

#### 3NF (Third Normal Form) ✅
- Meets 2NF requirements
- No transitive dependencies
- All non-key attributes directly dependent on primary key

### Denormalization Decisions

**Items in Plans Table (JSON)**
- Stored as JSON for flexibility
- Trade-off: Query complexity vs. schema flexibility
- Justification: Menu items vary by plan, JSON allows dynamic structure

**Billing Period in Payment_Logs**
- Redundant data (also in Bills table)
- Justification: Audit trail should be self-contained
- Improves query performance for reports



---

## 5.7 Sample Data and Queries

### Sample Data

#### Users Table
```sql
INSERT INTO users (fullname, email, phone, password, addr1, area, city, state, pincode, is_admin)
VALUES 
('John Doe', 'john@example.com', '9876543210', 'hashed_password', 'Flat 101, Building A', 'Vashi', 'Navi Mumbai', 'Maharashtra', '400703', FALSE),
('Admin User', 'admin@tiffintrack.com', '9876543211', 'hashed_password', 'Office Address', 'Nerul', 'Navi Mumbai', 'Maharashtra', '400706', TRUE);
```

#### Plans Table
```sql
INSERT INTO plans (name, daily_rate, description, items, is_active)
VALUES 
('Veg Thali', 120, 'Complete vegetarian meal', '["Basmati Rice","Dal Tadka","Mixed Vegetable Curry","2 Rotis","Fresh Salad","Pickle"]', TRUE),
('Non-Veg Thali', 180, 'Delicious non-vegetarian meal', '["Basmati Rice","Dal","Chicken Curry","2 Rotis","Raita","Pickle"]', TRUE),
('Diet Special', 150, 'Low calorie, high protein meal', '["Brown Rice","Moong Dal","Steamed Vegetables","Sprouts Salad"]', TRUE);
```

### Common Queries

#### Get Active Subscriptions for Customer
```sql
SELECT cp.*, p.name, p.daily_rate
FROM customer_plans cp
JOIN plans p ON cp.plan_id = p.id
WHERE cp.customer_id = 1 
  AND cp.is_active = TRUE 
  AND cp.end_date >= CURRENT_DATE;
```

#### Calculate Monthly Bill
```sql
SELECT 
    u.id,
    u.fullname,
    COUNT(DISTINCT cp.id) as active_plans,
    SUM(DATEDIFF(cp.end_date, cp.start_date) + 1) as total_days,
    (SELECT COUNT(*) FROM paused_dates WHERE customer_id = u.id AND MONTH(pause_date) = 2) as paused_days,
    SUM((DATEDIFF(cp.end_date, cp.start_date) + 1) * p.daily_rate) as total_amount
FROM users u
JOIN customer_plans cp ON u.id = cp.customer_id
JOIN plans p ON cp.plan_id = p.id
WHERE cp.is_active = TRUE
GROUP BY u.id;
```

#### Get Unpaid Bills
```sql
SELECT b.*, u.fullname, u.email
FROM bills b
JOIN users u ON b.customer_id = u.id
WHERE b.is_paid = FALSE
ORDER BY b.created_at DESC;
```

#### Kitchen Report for Today
```sql
SELECT 
    p.name as plan_name,
    COUNT(DISTINCT cp.customer_id) as meal_count,
    u.area
FROM customer_plans cp
JOIN plans p ON cp.plan_id = p.id
JOIN users u ON cp.customer_id = u.id
WHERE cp.is_active = TRUE
  AND CURRENT_DATE BETWEEN cp.start_date AND cp.end_date
  AND cp.customer_id NOT IN (
      SELECT customer_id FROM paused_dates WHERE pause_date = CURRENT_DATE
  )
GROUP BY p.name, u.area
ORDER BY u.area, p.name;
```



---

## 5.8 Database Security

### Access Control
- **Admin Users**: Full access to all tables
- **Customer Users**: Limited access to own records only
- **Application Layer**: All database access through ORM (SQLAlchemy)
- **No Direct Access**: Users cannot directly query database

### Data Protection
- **Password Hashing**: Werkzeug security (PBKDF2)
- **SQL Injection Prevention**: Parameterized queries via ORM
- **Session Management**: Flask session with secure cookies
- **HTTPS**: All data transmission encrypted

### Backup Strategy
- **Daily Backups**: Automated PostgreSQL backups
- **Point-in-Time Recovery**: Transaction log backups
- **Offsite Storage**: Backups stored in separate location
- **Retention**: 30 days of daily backups

### Audit Trail
- **Payment Logs**: Immutable record of all transactions
- **Timestamps**: created_at on all tables
- **User Actions**: Logged in application layer
- **Compliance**: GDPR and data protection compliance



---

## 5.9 Performance Optimization

### Indexing Strategy
- **Primary Keys**: Automatically indexed
- **Foreign Keys**: Indexed for join performance
- **Frequently Queried Columns**: email, area, is_active, is_paid
- **Composite Indexes**: (customer_id, is_active), (month, year)
- **Date Columns**: Indexed for range queries

### Query Optimization
- **Eager Loading**: Use JOIN to reduce N+1 queries
- **Pagination**: Limit results for large datasets
- **Caching**: Session-based caching for user data
- **Connection Pooling**: Reuse database connections

### Database Configuration
- **PostgreSQL**: Primary database (Neon cloud)
- **SQLite**: Fallback for development
- **Connection Pool**: 5 connections, 30s timeout
- **Retry Logic**: 3 retries with exponential backoff

### Monitoring
- **Health Check**: /health endpoint
- **Query Logging**: Slow query detection
- **Connection Monitoring**: Pool usage tracking
- **Error Alerts**: Database connection failures



---

## 5.10 Database Migration Strategy

### Migration Tool
- **Flask-Migrate**: Alembic-based migrations
- **Version Control**: All migrations tracked in Git
- **Rollback Support**: Can revert to previous versions

### Migration Commands
```bash
# Create new migration
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Show current version
flask db current

# Show migration history
flask db history
```

### Migration Best Practices
- **Test First**: Test migrations on development database
- **Backup Before**: Always backup before production migration
- **Incremental**: Small, focused migrations
- **Reversible**: Include downgrade logic
- **Data Migration**: Separate data migrations from schema changes

---

## 5.11 Summary

### Database Statistics
- **Total Tables**: 8
- **Total Relationships**: 8 (1:N relationships)
- **Normalization Level**: 3NF
- **Primary Database**: PostgreSQL (Neon)
- **Fallback Database**: SQLite

### Key Features
- ✅ Role-based access control
- ✅ Referential integrity enforced
- ✅ Audit trail for payments
- ✅ Flexible meal plan structure (JSON)
- ✅ Automatic billing calculations
- ✅ Cutoff time enforcement
- ✅ Address change restrictions
- ✅ Payment integration (Stripe)

### Compliance
- ✅ ACID properties maintained
- ✅ Data integrity constraints
- ✅ Security best practices
- ✅ Backup and recovery strategy
- ✅ Performance optimization
- ✅ Scalability considerations

---

**Document Version**: 1.0  
**Last Updated**: February 20, 2026  
**Database Version**: PostgreSQL 14+  
**ORM**: SQLAlchemy 2.0+  
**Migration Tool**: Flask-Migrate (Alembic)
