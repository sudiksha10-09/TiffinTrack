from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ------------------------
# Home / Landing Page
# ------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ------------------------
# Login Page
# ------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # ✅ Temporary demo authentication
        if email == "admin@tiffintrack.com" and password == "admin123":
            return redirect(url_for("admin_dashboard"))

        elif email == "customer@example.com" and password == "customer123":
            return redirect(url_for("customers"))

        # ❌ Invalid credentials
        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ------------------------
# Register Page
# ------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Later you can save user to DB here
        return redirect(url_for("login"))

    return render_template("register.html")


# ------------------------
# Admin Dashboard
# ------------------------
@app.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")


# ------------------------
# Customer Management
# ------------------------
@app.route("/customers")
def customers():
    return render_template("customer_management.html")


# ------------------------
# App Runner
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)
