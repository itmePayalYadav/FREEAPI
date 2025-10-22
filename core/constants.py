# ====================================
# User Role Constants and Choices
# ====================================
ROLE_USER = "USER"
ROLE_ADMIN = "ADMIN"
ROLE_SUPERADMIN = "SUPERADMIN"

ROLE_CHOICES = [
    (ROLE_USER, "User"),
    (ROLE_ADMIN, "Admin"),
    (ROLE_SUPERADMIN, "SuperAdmin"),
]

# ====================================
# Login Types
# ====================================
LOGIN_EMAIL_PASSWORD = "EMAIL_PASSWORD"
LOGIN_GOOGLE = "GOOGLE"
LOGIN_GITHUB = "GITHUB"

LOGIN_TYPE_CHOICES = [
    (LOGIN_EMAIL_PASSWORD, "Email & Password"),
    (LOGIN_GOOGLE, "Google"),
    (LOGIN_GITHUB, "GitHub"),
]

# ====================================
# Todo List Priority Levels
# ====================================
PRIORITY_LOW = "Low"
PRIORITY_MEDIUM = "Medium"
PRIORITY_HIGH = "High"

PRIORITY_CHOICES = [
    (PRIORITY_LOW, "Low"),
    (PRIORITY_MEDIUM, "Medium"),
    (PRIORITY_HIGH, "High"),
]

# ====================================
# Reaction Types
# ====================================
LIKE = "like"
DISLIKE = "dislike"
LOVE = "love"

REACTION_CHOICES = [
    (LIKE, "Like"),
    (DISLIKE, "Dislike"),
    (LOVE, "Love"),
]

# ====================================
# Published Types
# ====================================
DRAFT = 'draft'
PUBLISHED = 'published'
ARCHIVED = 'archived'
STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (ARCHIVED, 'Archived'),
]

# ====================================
# Notification Types
# ====================================
LIKE_POST = "like_post"
LIKE_COMMENT = "like_comment"
COMMENT = "comment"
FOLLOW = "follow"
MENTION = "mention"

NOTIFICATION_TYPES = [
    (LIKE_POST, "Like Post"),
    (LIKE_COMMENT, "Like Comment"),
    (COMMENT, "Comment"),
    (FOLLOW, "Follow"),
    (MENTION, "Mention"),
]

# ===============================
# Address
# ===============================
ADDRESS_TYPES = [
    ("HOME", "Home"),
    ("WORK", "Work"),
    ("OTHER", "Other"),
]

# ===============================
# Product Variant
# ===============================
COLOR_CHOICES = [
    ("BLACK", "Black"),
    ("WHITE", "White"),
    ("RED", "Red"),
    ("BLUE", "Blue"),
    ("GREEN", "Green"),
    ("YELLOW", "Yellow"),
    ("ORANGE", "Orange"),
    ("PURPLE", "Purple"),
    ("PINK", "Pink"),
    ("BROWN", "Brown"),
    ("GREY", "Grey"),
    ("MULTICOLOR", "Multicolor"),
    ("GOLD", "Gold"),
    ("SILVER", "Silver"),
]

SIZE_CHOICES = [
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
]

# ===============================
# Coupon
# ===============================
DISCOUNT_TYPE_CHOICES = [
    ("PERCENTAGE", "Percentage"),
    ("FIXED", "Fixed Amount"),
]

# ===============================
# Order Status
# ===============================
ORDER_STATUS = [
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('SHIPPED', 'Shipped'),
    ('DELIVERED', 'Delivered'),
    ('CANCELLED', 'Cancelled'),
]

# ===============================
# Payment
# ===============================
PAYMENT_METHODS = [
    ("RAZORPAY", "Razorpay"),
    ("PAYPAL", "PayPal")
]

PAYMENT_STATUS = [
    ("PENDING", "Pending"),
    ("SUCCESS", "Success"),
    ("FAILED", "Failed"),
    ("REFUNDED", "Refunded"),
]
