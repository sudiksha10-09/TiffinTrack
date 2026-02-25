import re
import uuid

# -----------------------------
# USERNAME VALIDATION
# -----------------------------
def is_valid_username(username: str) -> bool:
    if not username:
        return False
    return len(username.strip()) >= 3


# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
def is_valid_password(password: str) -> bool:
    if not password:
        return False
    return len(password) >= 5


# -----------------------------
# EMAIL VALIDATION
# -----------------------------
def is_valid_email(email: str) -> bool:
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


# -----------------------------
# PRICE CALCULATION
# -----------------------------
def calculate_total_price(price: float, quantity: int) -> float:
    if price < 0 or quantity < 0:
        return 0
    return price * quantity


# -----------------------------
# ORDER ID GENERATOR
# -----------------------------
def generate_order_id() -> str:
    return str(uuid.uuid4())[:8]


# -----------------------------
# QUANTITY VALIDATION
# -----------------------------
def is_valid_quantity(qty: int) -> bool:
    return isinstance(qty, int) and qty > 0


# -----------------------------
# PHONE NUMBER VALIDATION
# -----------------------------
def is_valid_phone(phone: str) -> bool:
    if not phone:
        return False
    return phone.isdigit() and len(phone) == 10


# -----------------------------
# STRING CLEANER
# -----------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip().lower()
