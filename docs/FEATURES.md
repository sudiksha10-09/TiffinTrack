# TiffinTrack Features Documentation

Complete guide to all features and functionality.

## Table of Contents
1. [Multi-Plan System](#multi-plan-system)
2. [Billing & Payments](#billing--payments)
3. [Customer Features](#customer-features)
4. [Admin Features](#admin-features)

---

## Multi-Plan System

### Overview
Customers can subscribe to multiple meal plans simultaneously without disrupting existing subscriptions.

### Features
- ✅ Multiple active plans per customer
- ✅ Overlapping plan dates supported
- ✅ Running vs Upcoming plan categorization
- ✅ Cancel upcoming plans before they start
- ✅ Add new plans without affecting existing ones

### How It Works

**For Customers:**
1. Go to "Choose Plans"
2. Select multiple plans
3. Set dates for each plan
4. Complete payment
5. All plans activate automatically

**Plan States:**
- **Running**: Currently active (start_date ≤ today ≤ end_date)
- **Upcoming**: Scheduled for future (start_date > today)
- **Expired**: Automatically filtered out (end_date < today)

**Dashboard Display:**
```
Currently Running (2)
├─ Premium Lunch Plan (Jan 15 - Feb 28)
└─ Healthy Breakfast (Feb 01 - Feb 28)

Upcoming Plans (1)
└─ Weekend Special (Mar 01 - Mar 31) [Cancel button]
```

### Billing
- Automatically calculates across all active plans
- Handles overlapping plans correctly
- Subtracts paused days from all plans
- Shows accurate monthly estimates

---

## Billing & Payments

### Billing Actions

#### 1. Generate Bills
- Creates monthly bills for all active customers
- Based on meal plans and pause history
- Automatic calculation of billable days
- Handles multiple plans per customer

**Usage:**
1. Select month and year
2. Click "Generate Bills"
3. System creates bills automatically

#### 2. Send Reminders
- Sends email reminders to customers with unpaid bills
- Beautiful HTML email templates
- Personalized with customer details
- Tracks sent/failed count

**Requirements:**
- Email must be configured (see SETUP.md)
- SMTP settings in .env

**Email Includes:**
- Customer name
- Bill period and amount
- Direct payment link
- Professional branding

#### 3. Export Data
- Export billing data to CSV
- Multiple filter options
- Ready for Excel/accounting software

**Export Options:**
1. All Bills
2. Current Month Only
3. Paid Bills Only
4. Unpaid Bills Only

**CSV Includes:**
- Bill ID, Customer details
- Month, Year, Days, Amount
- Payment status and dates

#### 4. Analytics
- Detailed billing analytics
- Payment trends
- Revenue forecasting
- Customer insights

### Payment Integration

**Stripe Integration:**
- Secure payment processing
- Multiple payment methods
- Automatic receipt generation
- Payment history tracking

**Payment Flow:**
1. Customer views bill
2. Clicks "Pay Now"
3. Enters payment details
4. Stripe processes payment
5. Bill marked as paid
6. Receipt sent via email

---

## Customer Features

### Dashboard
- View all active plans (running & upcoming)
- Current month billing estimate
- Paused days count
- Recent activity
- Quick actions

### Plan Management
- Browse available plans
- Subscribe to multiple plans
- Set custom date ranges
- Cancel upcoming plans
- View plan history

### Pause Calendar
- Pause meals for specific dates
- Cutoff time: 8:00 AM
- Automatic billing adjustment
- Remove paused dates
- Visual calendar interface

### Profile Management
- Update personal information
- Change password
- Update delivery address
- View subscription history

**Address Restrictions:**
- Cannot change address during active plans
- Visual indicators for locked fields
- Clear warning messages

### Billing
- View unpaid bills
- Payment history
- Current month estimate
- Pay bills online
- Download receipts

---

## Admin Features

### Dashboard
- Overview of all metrics
- Active customers count
- Revenue statistics
- Recent activity
- Quick actions

### Plan Management
- Create new meal plans
- Edit existing plans
- Upload plan images
- Set daily rates
- Activate/deactivate plans
- Delete unused plans

**Plan Form:**
- Name and description (unlimited length)
- Daily rate
- Menu items list
- Image upload
- Character counter for description

### Customer Management
- View all customers
- Customer details
- Subscription history
- Billing information
- Contact details

### Bill Management
- Generate monthly bills
- Send payment reminders
- Export billing data
- View payment history
- Mark bills as paid
- Analytics dashboard

### Kitchen Report
- Daily meal preparation list
- Grouped by plan
- Customer details
- Delivery addresses
- Pause status

### Delivery Routes
- Optimized delivery routes
- Grouped by area
- Customer addresses
- Contact information
- Active orders only

### Analytics
- Revenue trends
- Customer growth
- Payment analytics
- Plan popularity
- Retention metrics

---

## Technical Features

### Security
- Password hashing (Werkzeug)
- Session management
- CSRF protection
- SQL injection prevention
- XSS protection

### Database
- PostgreSQL with SQLAlchemy
- Automatic migrations (Alembic)
- Connection retry logic
- Data integrity constraints

### Email System
- SMTP integration
- HTML email templates
- Plain text fallback
- Error handling
- Multiple provider support

### Payment Processing
- Stripe integration
- Secure payment handling
- Webhook support
- Payment logging
- Automatic reconciliation

### File Upload
- Image upload for plans
- Automatic resizing
- File type validation
- Size limits (16MB)
- Secure storage

### Responsive Design
- Mobile-friendly interface
- Touch-optimized
- Bottom navigation on mobile
- Adaptive layouts
- Fast loading

---

## Business Rules

### Plans
- Plans must have positive daily rate
- Plan names must be unique
- Images are optional
- Descriptions can be unlimited length

### Subscriptions
- Start date cannot be in the past
- End date must be after start date
- Multiple plans can overlap
- Plans auto-expire after end date

### Pausing
- Cutoff time: 8:00 AM
- Cannot pause past dates
- Cannot pause today after cutoff
- Paused days reduce billing

### Billing
- Bills generated monthly
- Based on active days minus paused days
- Multiple plans calculated together
- Payment required before next month

### Payments
- Stripe handles all transactions
- Automatic bill marking
- Payment history maintained
- Receipts generated

---

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Customer
- `GET /dashboard` - Customer dashboard
- `GET /plans` - Browse plans
- `POST /plans/subscribe` - Subscribe to plans
- `GET /pause` - Pause calendar
- `POST /pause/save` - Save pause dates
- `GET /billing` - View bills
- `GET /profile` - User profile

### Admin
- `GET /admin` - Admin dashboard
- `GET /admin/plans` - Manage plans
- `POST /admin/plans/add` - Add plan
- `POST /admin/plans/edit/<id>` - Edit plan
- `GET /bills` - Bill management
- `POST /bills/generate/<month>/<year>` - Generate bills
- `POST /bills/send-reminders` - Send reminders
- `GET /bills/export` - Export data
- `GET /analytics` - Analytics dashboard

### Payments
- `POST /create-payment-intent` - Create payment
- `POST /payment-success` - Handle success
- `POST /payment-webhook` - Stripe webhook

---

## Future Enhancements

### Planned Features
1. SMS notifications
2. WhatsApp integration
3. Mobile app
4. Loyalty program
5. Referral system
6. Subscription auto-renewal
7. Custom meal preferences
8. Dietary restrictions
9. Feedback system
10. Rating & reviews

---

**Last Updated:** February 24, 2026
**Version:** 3.0
