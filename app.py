
import os
import re
from functools import wraps
from datetime import date, datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import get_db_connection, init_db


app = Flask(__name__)

# Development fallback only.
# Set SECRET_KEY in your environment for deployment.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-change-this-secret"
)

init_db()


# -------------------- LOGIN DECORATOR --------------------

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view


# -------------------- ADMIN DECORATOR --------------------

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))

        connection = get_db_connection()

        try:
            user = connection.execute(
                "SELECT role FROM users WHERE id = ?",
                (session["user_id"],)
            ).fetchone()
        finally:
            connection.close()

        if user is None:
            session.clear()
            flash("Please log in again.", "warning")
            return redirect(url_for("login"))

        if user["role"] != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard"))

        return view(*args, **kwargs)

    return wrapped_view


# -------------------- HOME PAGE --------------------

@app.route("/")
def home():
    return render_template("home.html")


# -------------------- EQUIPMENT PAGE --------------------

@app.route("/equipment")
def equipment():
    connection = get_db_connection()

    try:
        items = connection.execute("""
            SELECT id, name, category, description,
                   'Available' AS status
            FROM equipment
            WHERE is_active = 1
            ORDER BY name
        """).fetchall()
    finally:
        connection.close()

    return render_template("equipment.html", items=items)


# -------------------- STUDENT REGISTRATION --------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if (
            not name
            or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
            or len(password) < 8
        ):
            flash(
                "Enter a valid name and email, and a password "
                "of at least 8 characters.",
                "danger"
            )
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        connection = get_db_connection()

        try:
            connection.execute("""
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
            """, (name, email, password_hash))

            connection.commit()

        except Exception:
            connection.rollback()
            flash(
                "This email may already be registered. "
                "Please try another email.",
                "danger"
            )
            return render_template("register.html")

        finally:
            connection.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# -------------------- LOGIN --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_db_connection()

        try:
            user = connection.execute("""
                SELECT id, name, email, password_hash, role
                FROM users
                WHERE email = ?
            """, (email,)).fetchone()
        finally:
            connection.close()

        if user and check_password_hash(
            user["password_hash"], password
        ):
            session.clear()
            session["user_id"] = user["id"]

            flash("Login successful.", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin_bookings"))

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# -------------------- STUDENT DASHBOARD --------------------

@app.route("/dashboard")
@login_required
def dashboard():
    connection = get_db_connection()

    try:
        user = connection.execute("""
            SELECT id, name, email, role
            FROM users
            WHERE id = ?
        """, (session["user_id"],)).fetchone()
    finally:
        connection.close()

    if user is None:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)


# -------------------- LOGOUT --------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("home"))


# -------------------- BOOK EQUIPMENT --------------------

@app.route("/book/<int:equipment_id>", methods=["GET", "POST"])
@login_required
def book_equipment(equipment_id):
    connection = get_db_connection()

    try:
        item = connection.execute("""
            SELECT id, name, category, description
            FROM equipment
            WHERE id = ? AND is_active = 1
        """, (equipment_id,)).fetchone()

        if item is None:
            flash("Equipment not found.", "danger")
            return redirect(url_for("equipment"))

        if request.method == "POST":
            booking_date = request.form.get(
                "booking_date", ""
            ).strip()
            start_time = request.form.get(
                "start_time", ""
            ).strip()
            end_time = request.form.get(
                "end_time", ""
            ).strip()

            try:
                selected_date = date.fromisoformat(booking_date)
                start = datetime.strptime(
                    start_time, "%H:%M"
                ).time()
                end = datetime.strptime(
                    end_time, "%H:%M"
                ).time()

            except ValueError:
                flash("Enter a valid date and time.", "danger")
                return redirect(url_for(
                    "book_equipment",
                    equipment_id=equipment_id
                ))

            if selected_date < date.today() or start >= end:
                flash(
                    "Choose a valid date and time range.",
                    "danger"
                )
                return redirect(url_for(
                    "book_equipment",
                    equipment_id=equipment_id
                ))

            # Pending and Approved bookings block overlapping slots.
            conflict = connection.execute("""
                SELECT id
                FROM bookings
                WHERE equipment_id = ?
                  AND booking_date = ?
                  AND status IN ('Pending', 'Approved')
                  AND start_time < ?
                  AND end_time > ?
                LIMIT 1
            """, (
                equipment_id,
                booking_date,
                end_time,
                start_time
            )).fetchone()

            if conflict:
                flash(
                    "That time slot conflicts with an existing "
                    "pending or approved booking.",
                    "danger"
                )
                return redirect(url_for(
                    "book_equipment",
                    equipment_id=equipment_id
                ))

            connection.execute("""
                INSERT INTO bookings (
                    user_id,
                    equipment_id,
                    booking_date,
                    start_time,
                    end_time,
                    status
                )
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (
                session["user_id"],
                equipment_id,
                booking_date,
                start_time,
                end_time
            ))

            connection.commit()

            flash(
                "Booking request submitted successfully.",
                "success"
            )
            return redirect(url_for("my_bookings"))

    finally:
        connection.close()

    return render_template(
        "book_equipment.html",
        item=item,
        today=date.today().isoformat()
    )


# -------------------- MY BOOKINGS --------------------

@app.route("/my-bookings")
@login_required
def my_bookings():
    connection = get_db_connection()

    try:
        bookings = connection.execute("""
            SELECT
                b.id,
                e.name,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status
            FROM bookings b
            JOIN equipment e ON e.id = b.equipment_id
            WHERE b.user_id = ?
            ORDER BY b.booking_date DESC, b.start_time DESC
        """, (session["user_id"],)).fetchall()
    finally:
        connection.close()

    return render_template("bookings.html", bookings=bookings)


# -------------------- ADMIN: VIEW ALL BOOKINGS --------------------

@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    connection = get_db_connection()

    try:
        bookings = connection.execute("""
            SELECT
                b.id,
                u.name AS student_name,
                u.email AS student_email,
                e.name AS equipment_name,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status,
                b.created_at
            FROM bookings b
            JOIN users u ON u.id = b.user_id
            JOIN equipment e ON e.id = b.equipment_id
            ORDER BY
                CASE WHEN b.status = 'Pending' THEN 0 ELSE 1 END,
                b.booking_date DESC,
                b.start_time
        """).fetchall()
    finally:
        connection.close()

    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )


# -------------------- ADMIN: APPROVE BOOKING --------------------

@app.route(
    "/admin/bookings/<int:booking_id>/approve",
    methods=["POST"]
)
@admin_required
def approve_booking(booking_id):
    connection = get_db_connection()

    try:
        booking = connection.execute("""
            SELECT
                id,
                equipment_id,
                booking_date,
                start_time,
                end_time,
                status
            FROM bookings
            WHERE id = ?
        """, (booking_id,)).fetchone()

        if booking is None:
            flash("Booking request not found.", "danger")

        elif booking["status"] != "Pending":
            flash("This booking is no longer pending.", "warning")

        else:
            # Check again for a conflict before approval.
            conflict = connection.execute("""
                SELECT id
                FROM bookings
                WHERE equipment_id = ?
                  AND booking_date = ?
                  AND status = 'Approved'
                  AND id != ?
                  AND start_time < ?
                  AND end_time > ?
                LIMIT 1
            """, (
                booking["equipment_id"],
                booking["booking_date"],
                booking_id,
                booking["end_time"],
                booking["start_time"]
            )).fetchone()

            if conflict:
                flash(
                    "Cannot approve: another approved booking "
                    "uses this time slot.",
                    "danger"
                )
            else:
                connection.execute("""
                    UPDATE bookings
                    SET status = 'Approved'
                    WHERE id = ? AND status = 'Pending'
                """, (booking_id,))

                connection.commit()
                flash("Booking approved successfully.", "success")

    finally:
        connection.close()

    return redirect(url_for("admin_bookings"))


# -------------------- ADMIN: REJECT BOOKING --------------------

@app.route(
    "/admin/bookings/<int:booking_id>/reject",
    methods=["POST"]
)
@admin_required
def reject_booking(booking_id):
    connection = get_db_connection()

    try:
        booking = connection.execute("""
            SELECT id, status
            FROM bookings
            WHERE id = ?
        """, (booking_id,)).fetchone()

        if booking is None:
            flash("Booking request not found.", "danger")

        elif booking["status"] != "Pending":
            flash("This booking is no longer pending.", "warning")

        else:
            connection.execute("""
                UPDATE bookings
                SET status = 'Rejected'
                WHERE id = ? AND status = 'Pending'
            """, (booking_id,))

            connection.commit()
            flash("Booking rejected.", "success")

    finally:
        connection.close()

    return redirect(url_for("admin_bookings"))


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
