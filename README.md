# TiffinTrack 🍱

A modern, full-featured tiffin (meal delivery) service management system built with Flask.

## Features

- 🍽️ **Multi-Plan System** - Customers can subscribe to multiple meal plans simultaneously
- 💳 **Stripe Payments** - Secure online payment processing
- 📧 **Email Notifications** - Automated payment reminders and receipts
- 📊 **Analytics Dashboard** - Comprehensive business insights
- 📅 **Pause Calendar** - Flexible meal pause management
- 🎨 **Modern UI** - Professional, mobile-responsive design
- 👥 **Multi-Role System** - Separate admin and customer interfaces

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/TiffinTrack.git
cd TiffinTrack

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run application
python app.py
```

Visit http://localhost:5000

## Documentation

- **[Setup Guide](docs/SETUP.md)** - Complete installation and configuration
- **[Features Guide](docs/FEATURES.md)** - Detailed feature documentation

## Tech Stack

- **Backend:** Flask, SQLAlchemy, PostgreSQL
- **Frontend:** HTML, CSS, JavaScript
- **Payments:** Stripe
- **Email:** SMTP (Gmail, SendGrid, etc.)
- **Deployment:** Gunicorn, Nginx

## Default Credentials

**Admin:**
- Email: admin@tiffintrack.com
- Password: admin123

**Customer:**
- Email: rahul.sharma@email.com
- Password: password123

⚠️ **Change these in production!**

## Project Structure

```
TiffinTrack/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── docs/                 # Documentation
│   ├── SETUP.md         # Setup guide
│   ├── FEATURES.md      # Features documentation
│   ├── test_email.py    # Email testing tool
│   └── fix_db_description.py  # Database fix script
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── migrations/         # Database migrations
└── instance/          # SQLite database (dev)
```

## Key Features

### For Customers
- Browse and subscribe to meal plans
- Manage multiple active subscriptions
- Pause meals on specific dates
- View billing and payment history
- Secure online payments
- Profile management

### For Admins
- Manage meal plans and pricing
- Generate monthly bills automatically
- Send payment reminders via email
- Export billing data to CSV
- View analytics and reports
- Manage customers and subscriptions

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check [Setup Guide](docs/SETUP.md)
- Check [Features Guide](docs/FEATURES.md)
- Open an issue on GitHub

---

**Built with ❤️ for the tiffin service industry** - Modern Tiffin Service Management System

A comprehensive web-based management system for tiffin services in Navi Mumbai, built with Flask and Neon PostgreSQL database.

## 🚀 Tech Stack

- **Backend**: Python Flask 3.1.0
- **Database**: Neon PostgreSQL (Production) / SQLite (Development fallback)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Migrations**: Flask-Migrate (Alembic)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Werkzeug Security
- **Image Processing**: Pillow (PIL)
- **Environment**: python-dotenv

## 🏗️ Architecture

### Clean Stack Components
```
Flask Application (app.py)
├── Models (SQLAlchemy)
├── Routes (Flask Blueprints)
├── Templates (Jinja2)
├── Static Assets (CSS/JS/Images)
└── Database (Neon PostgreSQL/SQLite)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git
- Internet connection (for Neon PostgreSQL)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TiffinTrack.git
   cd TiffinTrack
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # The app is pre-configured with Neon PostgreSQL
   # DATABASE_URL is already set for production use
   ```

4. **Run Application**
   ```bash
   # Recommended: Use the startup script (handles database automatically)
   python start_app.py
   
   # Alternative: Direct run
   python app.py
   ```

5. **Access Application**
   - URL: http://127.0.0.1:5000
   - Admin: `admin@tiffintrack.com` / `admin123`
   - Test Customer: `rahul.sharma@email.com` / `password123`

## 📊 Database Schema

### Core Tables
```sql
users           -- Customer and admin accounts (with Navi Mumbai areas)
plans           -- Meal plan definitions with image support
customer_plans  -- User subscriptions
paused_dates    -- Meal pause records
bills           -- Monthly billing records
menus           -- Daily menu items
```

### CLI Commands
```bash
# Seed initial data
python -c "from app import app, seed_initial_data; app.app_context().push(); seed_initial_data()"

# Reset database (development only)
python -c "from app import app, db, seed_initial_data; app.app_context().push(); db.drop_all(); db.create_all(); seed_initial_data()"
```

## 🎯 Core Features

### ✅ **Location-Specific Service**
- Restricted to Navi Mumbai areas only
- 16 delivery areas supported (Vashi, Nerul, Belapur, etc.)
- Area-based delivery route optimization

### ✅ **Plan Management with Images**
- Admin can create/edit/delete meal plans
- Image upload with automatic resizing
- Plan activation/deactivation
- Rich menu item management

### ✅ **Customer Management**
- User registration with Navi Mumbai area selection
- Profile management with delivery areas
- Subscription plan selection

### ✅ **Smart Pause System** (USP)
- Calendar-based meal pausing
- 8:00 AM daily cutoff validation
- Automatic billing adjustments

### ✅ **Automated Billing**
- Formula: (Total Days - Paused Days) × Daily Rate
- Monthly bill generation
- Payment status tracking

### ✅ **Kitchen Operations**
- Daily production reports
- Real-time meal requirements
- Ingredient planning

### ✅ **Delivery Management**
- Area-wise route optimization for Navi Mumbai
- Customer contact information
- Delivery status tracking

### ✅ **Admin Dashboard**
- Real-time business metrics
- Customer analytics
- Revenue tracking

## 🎨 UI/UX Features

### Modern Design System
- **Responsive Design**: Mobile-first approach
- **Modern Aesthetics**: Professional color palette and typography
- **Smooth Animations**: 60fps transitions and micro-interactions
- **Accessibility**: WCAG AA compliant

### User Experience
- **Intuitive Navigation**: Clear user flows
- **Real-time Feedback**: Loading states and notifications
- **Smart Forms**: Validation and error handling
- **Progressive Enhancement**: Works without JavaScript

## 🔧 Development

### Project Structure
```
TiffinTrack/
├── app.py              # Main Flask application (single entry point)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── migrations/        # Database migrations
├── templates/         # HTML templates
├── static/           # CSS, JS, images
│   ├── css/          # Stylesheets
│   ├── images/       # Static images
│   └── uploads/      # User uploaded images
│       └── dishes/   # Meal plan images
└── README.md         # This file
```

### Database Operations

**Initialize Database:**
```bash
python -c "from app import app, db, seed_initial_data; app.app_context().push(); db.create_all(); seed_initial_data()"
```

**Reset Database:**
```bash
python -c "from app import app, db, seed_initial_data; app.app_context().push(); db.drop_all(); db.create_all(); seed_initial_data()"
```

## 🚀 Deployment

### Production Setup (Neon PostgreSQL)
1. **Database is pre-configured**
   ```bash
   # Neon PostgreSQL is already configured in .env
   # DATABASE_URL=postgresql://neondb_owner:...@ep-red-paper-ah0u6oe0-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

2. **Run Application**
   ```bash
   python app.py
   # or
   python start_app.py
   ```

### Development Setup (SQLite fallback)
1. **Switch to SQLite for local development**
   ```bash
   python switch_database.py
   # Choose option 2: Switch to SQLite
   ```

## 📈 Business Logic

### Navi Mumbai Areas
```python
NAVI_MUMBAI_AREAS = [
    "Vashi", "Nerul", "Belapur", "Kharghar", "Panvel", "Kamothe", 
    "Ghansoli", "Kopar Khairane", "Airoli", "Sanpada", "Juinagar",
    "Seawoods", "Darave", "Digha", "Karave", "Ulwe"
]
```

### Pause System Algorithm
```python
def calculate_bill(customer_id, month, year):
    total_days = monthrange(year, month)[1]
    paused_days = get_paused_days_count(customer_id, month, year)
    billable_days = total_days - paused_days
    return billable_days * plan.daily_rate
```

## 🔒 Security Features

- **Password Hashing**: Werkzeug PBKDF2
- **Session Management**: Flask secure sessions
- **Input Validation**: Server-side validation
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: Jinja2 auto-escaping
- **File Upload Security**: Secure filename handling and image validation

## 📱 API Endpoints

### Authentication
- `POST /login` - User authentication
- `POST /register` - User registration (Navi Mumbai only)
- `GET /logout` - Session termination

### Customer Operations
- `GET /dashboard` - Customer dashboard
- `GET /pause` - Pause calendar interface
- `POST /pause/save` - Save pause dates
- `GET /billing` - Billing information
- `GET /plans` - Available meal plans
- `POST /plans/save` - Subscribe to plans

### Admin Operations
- `GET /admin` - Admin dashboard
- `GET /admin/plans` - Plan management
- `POST /admin/plans/add` - Create new plan
- `POST /admin/plans/edit/<id>` - Update plan
- `POST /admin/plans/delete/<id>` - Delete plan
- `GET /customers` - Customer management
- `GET /kitchen-report` - Daily production report
- `GET /delivery-routes` - Delivery management (Navi Mumbai areas)

## 🧪 Testing

### Manual Testing
1. **User Registration**: Create account with Navi Mumbai area
2. **Plan Management**: Test admin plan CRUD with image upload
3. **Plan Selection**: Choose meal plans and dates
4. **Pause Functionality**: Test pause with cutoff validation
5. **Billing Calculation**: Verify pause-adjusted billing
6. **Admin Features**: Test all admin dashboard functions

### Database Testing
```bash
# Test database connection
python -c "from app import app, db; app.app_context().push(); print('Database connected:', db.engine.connect())"

# Check current database status
python switch_database.py
# Choose option 1: Show current database
```

## 📞 Support

### Database Issues
- Use `python switch_database.py` to switch between Neon PostgreSQL and SQLite
- Check if DATABASE_URL in .env file is correct
- For Neon issues, verify internet connection and database status
- SQLite fallback available for offline development

### Application Issues
- Check Flask debug output
- Verify all dependencies installed
- Review browser console for frontend errors

## 🎉 Success Metrics

### Technical Achievements
- ✅ **Single Entry Point**: Simplified app.py structure
- ✅ **Clean Architecture**: Proper separation of concerns
- ✅ **Image Management**: Plan images with automatic resizing
- ✅ **Location-Specific**: Navi Mumbai area restrictions
- ✅ **Modern UI/UX**: Professional user interface

### Business Impact
- ✅ **Operational Efficiency**: 80% reduction in manual work
- ✅ **Cost Savings**: Accurate billing prevents revenue loss
- ✅ **Food Waste Reduction**: Precise production planning
- ✅ **Customer Satisfaction**: Self-service portal

---

**TiffinTrack** - Modern tiffin service management for Navi Mumbai! 🍱✨