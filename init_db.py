import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "raytrace.db"


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Admin users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Site settings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS site_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT
        )
    """)

    # Homepage content
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS homepage_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            title TEXT,
            content TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # About page content
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS about_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Products
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            price TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Achievements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Employees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    # Contact messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Default admin user
    default_username = "admin"
    default_password = "admin123"
    password_hash = generate_password_hash(default_password)

    cursor.execute("SELECT * FROM admin_users WHERE username = ?", (default_username,))
    existing_admin = cursor.fetchone()

    if not existing_admin:
        cursor.execute("""
            INSERT INTO admin_users (username, password_hash)
            VALUES (?, ?)
        """, (default_username, password_hash))

    # Default site settings
    default_settings = [
        ("site_name", "RayTrace Labs"),
        ("site_tagline", "Robotics, Embedded Systems, AI & Intelligent Engineering Solutions"),
        ("site_location", "Rajshahi, Bangladesh"),
        ("contact_email", "info@raytracelabs.com"),
        ("contact_phone", "+880 1XXX-XXXXXX"),
        ("contact_address", "Rajshahi, Bangladesh"),
    ]

    for key, value in default_settings:
        cursor.execute("SELECT id FROM site_settings WHERE key = ?", (key,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(
                "INSERT INTO site_settings (key, value) VALUES (?, ?)",
                (key, value)
            )

    # Default homepage content
    default_homepage_sections = [
        ("hero_title", "RayTrace Labs", "Professional engineering for robotics, embedded systems, AI, and IoT."),
        ("hero_subtitle", "Engineering Innovation", "Premium technology solutions built for real-world deployment."),
        ("about_preview", "Who We Are", "RayTrace Labs develops practical, research-driven engineering systems."),
    ]

    for section, title, content in default_homepage_sections:
        cursor.execute("SELECT id FROM homepage_content WHERE section = ?", (section,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("""
                INSERT INTO homepage_content (section, title, content)
                VALUES (?, ?, ?)
            """, (section, title, content))

    conn.commit()
    conn.close()

    print("Database initialized successfully.")
    print("Default admin username: admin")
    print("Default admin password: admin123")


if __name__ == "__main__":
    init_database()