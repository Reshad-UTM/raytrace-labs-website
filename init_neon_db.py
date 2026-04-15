import os
import psycopg2
from werkzeug.security import generate_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS site_settings (
    id SERIAL PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS homepage_content (
    id SERIAL PRIMARY KEY,
    section TEXT NOT NULL UNIQUE,
    title TEXT,
    content TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    price TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    date TEXT,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    designation TEXT,
    department TEXT,
    email TEXT,
    phone TEXT,
    joining_date TEXT,
    bio TEXT,
    skills TEXT,
    photo_path TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS contact_messages (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

admin_username = "reshadadmin"
admin_password = "ChangeThisNow123!"
password_hash = generate_password_hash(admin_password)

cur.execute("SELECT id FROM admin_users WHERE username = %s", (admin_username,))
if not cur.fetchone():
    cur.execute(
        "INSERT INTO admin_users (username, password_hash) VALUES (%s, %s)",
        (admin_username, password_hash)
    )

defaults = [
    ("site_name", "RayTrace Labs"),
    ("site_tagline", "Robotics, Embedded Systems, AI & Intelligent Engineering Solutions"),
    ("site_location", "Rajshahi, Bangladesh"),
    ("footer_text", "© 2026 RayTrace Labs. All rights reserved."),
    ("contact_email", "info@raytracelabs.com"),
    ("contact_phone", "+880 1XXX-XXXXXX"),
    ("contact_address", "Rajshahi, Bangladesh"),
]

for key, value in defaults:
    cur.execute("SELECT id FROM site_settings WHERE key = %s", (key,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO site_settings (key, value) VALUES (%s, %s)",
            (key, value)
        )

conn.commit()
cur.close()
conn.close()

print("Neon database initialized successfully.")