from utils import (
    is_valid_username,
    is_valid_password,
    is_valid_email,
    calculate_total_price,
    generate_order_id,
    is_valid_quantity,
    is_valid_phone,
    clean_text
)

# -----------------------------
# USERNAME TESTS
# -----------------------------
def test_valid_username():
    assert is_valid_username("sudi") == True

def test_invalid_username_short():
    assert is_valid_username("ab") == False

def test_invalid_username_empty():
    assert is_valid_username("") == False


# -----------------------------
# PASSWORD TESTS
# -----------------------------
def test_valid_password():
    assert is_valid_password("12345") == True

def test_invalid_password_short():
    assert is_valid_password("123") == False


# -----------------------------
# EMAIL TESTS
# -----------------------------
def test_valid_email():
    assert is_valid_email("test@gmail.com") == True

def test_invalid_email_no_at():
    assert is_valid_email("testgmail.com") == False

def test_invalid_email_empty():
    assert is_valid_email("") == False


# -----------------------------
# PRICE CALCULATION TESTS
# -----------------------------
def test_total_price_correct():
    assert calculate_total_price(50, 2) == 100

def test_total_price_zero_quantity():
    assert calculate_total_price(50, 0) == 0

def test_total_price_negative():
    assert calculate_total_price(-10, 5) == 0


# -----------------------------
# ORDER ID TEST
# -----------------------------
def test_generate_order_id_length():
    order_id = generate_order_id()
    assert len(order_id) == 8

def test_generate_order_id_unique():
    id1 = generate_order_id()
    id2 = generate_order_id()
    assert id1 != id2


# -----------------------------
# QUANTITY TESTS
# -----------------------------
def test_valid_quantity():
    assert is_valid_quantity(3) == True

def test_invalid_quantity_zero():
    assert is_valid_quantity(0) == False

def test_invalid_quantity_negative():
    assert is_valid_quantity(-2) == False


# -----------------------------
# PHONE TESTS
# -----------------------------
def test_valid_phone():
    assert is_valid_phone("9876543210") == True

def test_invalid_phone_letters():
    assert is_valid_phone("98AB543210") == False

def test_invalid_phone_length():
    assert is_valid_phone("12345") == False


# -----------------------------
# CLEAN TEXT TESTS
# -----------------------------
def test_clean_text_spaces():
    assert clean_text("  Hello  ") == "hello"

def test_clean_text_empty():
    assert clean_text("") == ""
