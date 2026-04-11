import os
from functools import wraps
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from database import execute_query, query_all, query_one

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-later-raytrace-secret-key")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

@app.context_processor
def inject_site_data():
    return {
        "global_site_name": "RayTrace Labs",
        "global_site_tagline": "Robotics, Embedded Systems, AI & Intelligent Engineering Solutions",
        "global_site_location": "Rajshahi, Bangladesh",
        "global_footer_text": "© 2026 RayTrace Labs. All rights reserved.",
    }


def get_setting(key, default_value=""):
    row = query_one("SELECT value FROM site_settings WHERE key = ?", (key,))
    return row["value"] if row else default_value


def set_setting(key, value):
    existing = query_one("SELECT id FROM site_settings WHERE key = ?", (key,))
    if existing:
        execute_query(
            "UPDATE site_settings SET value = ? WHERE key = ?",
            (value, key)
        )
    else:
        execute_query(
            "INSERT INTO site_settings (key, value) VALUES (?, ?)",
            (key, value)
        )


def get_homepage_section(section_name, default_title="", default_content=""):
    row = query_one(
        "SELECT * FROM homepage_content WHERE section = ?",
        (section_name,)
    )
    if row:
        return {
            "title": row["title"] or default_title,
            "content": row["content"] or default_content,
        }
    return {"title": default_title, "content": default_content}


def upsert_homepage_section(section_name, title, content):
    existing = query_one(
        "SELECT id FROM homepage_content WHERE section = ?",
        (section_name,)
    )

    if existing:
        execute_query(
            """
            UPDATE homepage_content
            SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE section = ?
            """,
            (title, content, section_name)
        )
    else:
        execute_query(
            """
            INSERT INTO homepage_content (section, title, content)
            VALUES (?, ?, ?)
            """,
            (section_name, title, content)
        )


def admin_login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("home"))
        return view_func(*args, **kwargs)
    return wrapper


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_obj):
    return "" 


@app.route("/")
def home():
    company_info = {
        "name": "RayTrace Labs",
        "tagline": "Robotics, Embedded Systems, AI & Intelligent Engineering Solutions",
        "location": "Rajshahi, Bangladesh",
    }

    hero_section = "RayTrace Labs"
    hero_subtitle = "Engineering Innovation"
    about_preview = "RayTrace Labs develops practical, research-driven engineering systems."

    featured_domains = [
        {
            "title": "Robotics",
            "text": "Advanced robotic platforms for industrial, research, and field applications."
        },
        {
            "title": "Embedded Systems",
            "text": "Reliable firmware, control systems, sensor integration, and hardware interfacing."
        },
        {
            "title": "AI & Vision",
            "text": "Intelligent algorithms, computer vision, and data-driven smart systems."
        },
        {
            "title": "IoT & Automation",
            "text": "Connected monitoring, remote control, and industrial automation solutions."
        },
    ]

    featured_products = []
    achievements_preview = []
    team_preview = []

    return render_template(
        "index.html",
        company_info=company_info,
        hero_section=hero_section,
        hero_subtitle=hero_subtitle,
        about_preview=about_preview,
        featured_domains=featured_domains,
        featured_products=featured_products,
        achievements_preview=achievements_preview,
        team_preview=team_preview,
    )


@app.route("/about")
def about():
    about_data = {
        "title": "About RayTrace Labs",
        "intro": (
            "RayTrace Labs is a technology-driven engineering company focused on robotics, "
            "embedded systems, AI, industrial automation, and product innovation."
        ),
        "mission": (
            "To design reliable and intelligent engineering solutions that solve real-world "
            "problems with precision, efficiency, and innovation."
        ),
        "vision": (
            "To become a trusted technology and research partner in robotics, embedded intelligence, "
            "and advanced system development."
        ),
        "strengths": [
            "Research-driven product development",
            "End-to-end embedded and electronics integration",
            "Practical automation and intelligent systems engineering",
            "Scalable prototypes for industry and innovation",
        ],
    }
    return render_template("about.html", about_data=about_data)


@app.route("/products")
def products():
    products_data = query_all("SELECT * FROM products ORDER BY id DESC")
    return render_template("products.html", products_data=products_data)


@app.route("/achievements")
def achievements():
    achievements_data = query_all("SELECT * FROM achievements ORDER BY id DESC")
    return render_template("achievements.html", achievements_data=achievements_data)


@app.route("/employees")
def employees():
    employees_data = query_all(
        "SELECT * FROM employees WHERE is_active = 1 ORDER BY id DESC"
    )
    return render_template("employees.html", employees_data=employees_data)


@app.route("/employees/<int:employee_id>")
def employee_detail(employee_id):
    employee = query_one(
        "SELECT * FROM employees WHERE id = %s AND is_active = 1",
        (employee_id,)
    )

    if not employee:
        flash("Employee not found.", "error")
        return redirect(url_for("employees"))

    return render_template("employee_detail.html", employee=employee)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    company_contact = {
        "email": get_setting("contact_email", "info@raytracelabs.com"),
        "phone": get_setting("contact_phone", "+880 1XXX-XXXXXX"),
        "address": get_setting("contact_address", "Rajshahi, Bangladesh"),
    }

    form_data = {
        "name": "",
        "email": "",
        "subject": "",
        "message": "",
    }

    if request.method == "POST":
        form_data["name"] = request.form.get("name", "").strip()
        form_data["email"] = request.form.get("email", "").strip()
        form_data["subject"] = request.form.get("subject", "").strip()
        form_data["message"] = request.form.get("message", "").strip()

        if not form_data["name"]:
            flash("Name is required.", "error")
            return render_template("contact.html", company_contact=company_contact, form_data=form_data)

        if not form_data["email"]:
            flash("Email is required.", "error")
            return render_template("contact.html", company_contact=company_contact, form_data=form_data)

        if not form_data["message"]:
            flash("Message is required.", "error")
            return render_template("contact.html", company_contact=company_contact, form_data=form_data)

        execute_query(
            """
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
            """,
            (
                form_data["name"],
                form_data["email"],
                form_data["subject"],
                form_data["message"],
            )
        )

        flash("Your message has been sent successfully.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html", company_contact=company_contact, form_data=form_data)


@app.route("/secure-raytrace-admin-9921", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("admin/login.html")

        admin_user = query_one(
            "SELECT * FROM admin_users WHERE username = ?",
            (username,)
        )

        if admin_user and check_password_hash(admin_user["password_hash"], password):
            session["admin_logged_in"] = True
            session["admin_user_id"] = admin_user["id"]
            session["admin_username"] = admin_user["username"]

            flash("Login successful.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin/login.html")


@app.route("/admin/logout")
@admin_login_required
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_login_required
def admin_dashboard():
    stats = {
        "products_count": query_one("SELECT COUNT(*) AS count FROM products")["count"],
        "achievements_count": query_one("SELECT COUNT(*) AS count FROM achievements")["count"],
        "employees_count": query_one("SELECT COUNT(*) AS count FROM employees")["count"],
        "messages_count": query_one("SELECT COUNT(*) AS count FROM contact_messages")["count"],
    }

    recent_employees = query_all(
        "SELECT * FROM employees ORDER BY id DESC LIMIT 5"
    )

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_employees=recent_employees
    )


@app.route("/admin/settings", methods=["GET", "POST"])
@admin_login_required
def admin_settings():
    if request.method == "POST":
        set_setting("site_name", request.form.get("site_name", "").strip())
        set_setting("site_tagline", request.form.get("site_tagline", "").strip())
        set_setting("contact_email", request.form.get("contact_email", "").strip())
        set_setting("contact_phone", request.form.get("contact_phone", "").strip())
        set_setting("contact_address", request.form.get("contact_address", "").strip())
        set_setting("footer_text", request.form.get("footer_text", "").strip())
        set_setting("site_location", request.form.get("site_location", "").strip())

        flash("Site settings updated successfully.", "success")
        return redirect(url_for("admin_settings"))

    settings_data = {
        "site_name": get_setting("site_name", "RayTrace Labs"),
        "site_tagline": get_setting("site_tagline", "Robotics, Embedded Systems, AI & Intelligent Engineering Solutions"),
        "contact_email": get_setting("contact_email", "info@raytracelabs.com"),
        "contact_phone": get_setting("contact_phone", "+880 1XXX-XXXXXX"),
        "contact_address": get_setting("contact_address", "Rajshahi, Bangladesh"),
        "footer_text": get_setting("footer_text", "© 2026 RayTrace Labs. All rights reserved."),
        "site_location": get_setting("site_location", "Rajshahi, Bangladesh"),
    }

    return render_template("admin/settings.html", settings_data=settings_data)


@app.route("/admin/homepage", methods=["GET", "POST"])
@admin_login_required
def admin_homepage():
    if request.method == "POST":
        hero_title = request.form.get("hero_title", "").strip()
        hero_content = request.form.get("hero_content", "").strip()
        hero_subtitle_title = request.form.get("hero_subtitle_title", "").strip()
        hero_subtitle_content = request.form.get("hero_subtitle_content", "").strip()
        about_preview_title = request.form.get("about_preview_title", "").strip()
        about_preview_content = request.form.get("about_preview_content", "").strip()

        upsert_homepage_section("hero_title", hero_title, hero_content)
        upsert_homepage_section("hero_subtitle", hero_subtitle_title, hero_subtitle_content)
        upsert_homepage_section("about_preview", about_preview_title, about_preview_content)

        flash("Homepage content updated successfully.", "success")
        return redirect(url_for("admin_homepage"))

    homepage_data = {
        "hero_title": get_homepage_section(
            "hero_title",
            "RayTrace Labs",
            "Professional engineering for robotics, embedded systems, AI, and IoT."
        ),
        "hero_subtitle": get_homepage_section(
            "hero_subtitle",
            "Engineering Innovation",
            "Premium technology solutions built for real-world deployment."
        ),
        "about_preview": get_homepage_section(
            "about_preview",
            "Who We Are",
            "RayTrace Labs develops practical, research-driven engineering systems."
        ),
    }

    return render_template("admin/homepage.html", homepage_data=homepage_data)


@app.route("/admin/products")
@admin_login_required
def admin_products():
    products_data = query_all("SELECT * FROM products ORDER BY id DESC")
    return render_template("admin/products.html", products_data=products_data)


@app.route("/admin/products/add", methods=["GET", "POST"])
@admin_login_required
def admin_add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

        image_file = request.files.get("image")
        saved_image_name = save_uploaded_file(image_file)

        if saved_image_name is None:
            flash("Invalid image format. Use PNG, JPG, JPEG, or WEBP.", "error")
            return render_template("admin/product_form.html", form_mode="add", product=None)

        if not name:
            flash("Product name is required.", "error")
            return render_template("admin/product_form.html", form_mode="add", product=None)

        execute_query(
            "INSERT INTO products (name, description, category, icon) VALUES (?, ?, ?, ?)",
            (name, description, category, None)
        )

        flash("Product added successfully.", "success")
        return redirect(url_for("admin_products"))

    return render_template("admin/product_form.html", form_mode="add", product=None)


@app.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
@admin_login_required
def admin_edit_product(product_id):
    product = query_one("SELECT * FROM products WHERE id = %s", (product_id,))

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("admin_products"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

        current_image = product["icon"] or ""
        image_file = request.files.get("image")

        if image_file and image_file.filename:
            saved_image_name = save_uploaded_file(image_file)
            if saved_image_name is None:
                flash("Invalid image format. Use PNG, JPG, JPEG, or WEBP.", "error")
                return render_template("admin/product_form.html", form_mode="edit", product=product)
            current_image = saved_image_name

        execute_query(
            "UPDATE products SET name=?, description=?, category=?, icon=? WHERE id=?",
            (name, description, category, current_image, product_id)
        )

        flash("Product updated.", "success")
        return redirect(url_for("admin_products"))

    return render_template("admin/product_form.html", form_mode="edit", product=product)


@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@admin_login_required
def admin_delete_product(product_id):
    execute_query("DELETE FROM products WHERE id=?", (product_id,))
    flash("Product deleted.", "success")
    return redirect(url_for("admin_products"))


@app.route("/admin/achievements")
@admin_login_required
def admin_achievements():
    achievements_data = query_all("SELECT * FROM achievements ORDER BY id DESC")
    return render_template("admin/achievements.html", achievements_data=achievements_data)



@app.route("/admin/achievements/add", methods=["GET", "POST"])
@admin_login_required
def admin_add_achievement():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        date = request.form.get("date", "").strip()

        image_file = request.files.get("image")
        saved_image_name = save_uploaded_file(image_file)

        if saved_image_name is None:
            flash("Invalid image format. Use PNG, JPG, JPEG, or WEBP.", "error")
            return render_template("admin/achievement_form.html", form_mode="add", achievement=None)

        if not title:
            flash("Achievement title is required.", "error")
            return render_template("admin/achievement_form.html", form_mode="add", achievement=None)

        execute_query(
            "INSERT INTO achievements (title, description, date, image_path) VALUES (?, ?, ?, ?)",
            (title, description, date, saved_image_name)
        )

        flash("Achievement added successfully.", "success")
        return redirect(url_for("admin_achievements"))

    return render_template("admin/achievement_form.html", form_mode="add", achievement=None)



@app.route("/admin/achievements/edit/<int:achievement_id>", methods=["GET", "POST"])
@admin_login_required
def admin_edit_achievement(achievement_id):
    achievement = query_one("SELECT * FROM achievements WHERE id = %s", (achievement_id,))

    if not achievement:
        flash("Achievement not found.", "error")
        return redirect(url_for("admin_achievements"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        date = request.form.get("date", "").strip()

        if not title:
            flash("Achievement title is required.", "error")
            return render_template("admin/achievement_form.html", form_mode="edit", achievement=achievement)

        current_image = achievement["image_path"] or ""
        image_file = request.files.get("image")

        if image_file and image_file.filename:
            saved_image_name = save_uploaded_file(image_file)
            if saved_image_name is None:
                flash("Invalid image format. Use PNG, JPG, JPEG, or WEBP.", "error")
                return render_template("admin/achievement_form.html", form_mode="edit", achievement=achievement)
            current_image = saved_image_name

        execute_query(
            "UPDATE achievements SET title=?, description=?, date=?, image_path=? WHERE id=?",
            (title, description, date, current_image, achievement_id)
        )

        flash("Achievement updated successfully.", "success")
        return redirect(url_for("admin_achievements"))

    return render_template("admin/achievement_form.html", form_mode="edit", achievement=achievement)


@app.route("/admin/achievements/delete/<int:achievement_id>", methods=["POST"])
@admin_login_required
def admin_delete_achievement(achievement_id):
    execute_query("DELETE FROM achievements WHERE id=?", (achievement_id,))
    flash("Achievement deleted successfully.", "success")
    return redirect(url_for("admin_achievements"))


@app.route("/admin/messages")
@admin_login_required
def admin_messages():
    messages_data = query_all(
        "SELECT * FROM contact_messages ORDER BY id DESC"
    )
    return render_template("admin/messages.html", messages_data=messages_data)


@app.route("/admin/employees")
@admin_login_required
def admin_employees():
    employees_data = query_all("SELECT * FROM employees ORDER BY id DESC")
    return render_template("admin/employees.html", employees_data=employees_data)


@app.route("/admin/employees/add", methods=["GET", "POST"])
@admin_login_required
def admin_add_employee():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        designation = request.form.get("designation", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        joining_date = request.form.get("joining_date", "").strip()
        bio = request.form.get("bio", "").strip()
        skills = request.form.get("skills", "").strip()
        is_active = 1 if request.form.get("is_active") == "on" else 0

        photo_file = request.files.get("photo")
        saved_photo_name = save_uploaded_file(photo_file)

        if saved_photo_name is None:
            flash("Invalid image format. Use PNG, JPG, JPEG, or WEBP.", "error")
            return render_template(
                "admin/employee_form.html",
                form_mode="add",
                employee=None
            )

        if not name:
            flash("Employee name is required.", "error")
            return render_template(
                "admin/employee_form.html",
                form_mode="add",
                employee=None
            )

        execute_query(
            """
            INSERT INTO employees
            (name, designation, department, email, phone, joining_date, bio, skills, photo_path, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                designation,
                department,
                email,
                phone,
                joining_date,
                bio,
                skills,
                saved_photo_name,
                is_active
            )
        )

        flash("Employee added successfully.", "success")
        return redirect(url_for("admin_employees"))

    return render_template(
        "admin/employee_form.html",
        form_mode="add",
        employee=None
    )


@app.route("/admin/employees/edit/<int:employee_id>", methods=["GET", "POST"])
@admin_login_required
def admin_edit_employee(employee_id):
    employee = query_one("SELECT * FROM employees WHERE id = %s", (employee_id,))

    if not employee:
        flash("Employee not found.", "error")
        return redirect(url_for("admin_employees"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        designation = request.form.get("designation", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        joining_date = request.form.get("joining_date", "").strip()
        bio = request.form.get("bio", "").strip()
        skills = request.form.get("skills", "").strip()
        is_active = 1 if request.form.get("is_active") == "on" else 0

        if not name:
            flash("Employee name is required.", "error")
            return render_template(
                "admin/employee_form.html",
                form_mode="edit",
                employee=employee
            )

        current_photo = employee["photo_path"] or ""
        photo_file = request.files.get("photo")

        if photo_file and photo_file.filename:
            saved_photo_name = save_uploaded_file(photo_file)
            if saved_photo_name is None:
                flash("Invalid image format. Use PNG, JPG, JPEG, or WEBP.", "error")
                return render_template(
                    "admin/employee_form.html",
                    form_mode="edit",
                    employee=employee
                )
            current_photo = saved_photo_name

        execute_query(
            """
            UPDATE employees
            SET name = ?, designation = ?, department = ?, email = ?, phone = ?,
                joining_date = ?, bio = ?, skills = ?, photo_path = ?, is_active = ?
            WHERE id = %s
            """,
            (
                name,
                designation,
                department,
                email,
                phone,
                joining_date,
                bio,
                skills,
                current_photo,
                is_active,
                employee_id
            )
        )

        flash("Employee updated successfully.", "success")
        return redirect(url_for("admin_employees"))

    return render_template(
        "admin/employee_form.html",
        form_mode="edit",
        employee=employee
    )


@app.route("/admin/employees/delete/<int:employee_id>", methods=["POST"])
@admin_login_required
def admin_delete_employee(employee_id):
    employee = query_one("SELECT * FROM employees WHERE id = %s", (employee_id,))

    if not employee:
        flash("Employee not found.", "error")
        return redirect(url_for("admin_employees"))

    execute_query("DELETE FROM employees WHERE id = %s", (employee_id,))
    flash("Employee deleted successfully.", "success")
    return redirect(url_for("admin_employees"))


