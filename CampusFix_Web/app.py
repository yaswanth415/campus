import os
import sqlite3
from datetime import date
from functools import wraps
from io import BytesIO

import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file
)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "campus.db")

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "campusfix-secret-key-2026"
)


# ============================================================
# ADMIN LOGIN
# ============================================================

ADMIN_USERNAME = "Saicharan"
ADMIN_PASSWORD = "Charu12"


# ============================================================
# DROPDOWN OPTIONS
# ============================================================

CATEGORIES = [
    "Electrical",
    "Furniture",
    "Plumbing",
    "IT",
    "Internet",
    "Cleaning",
    "AC/Cooling",
    "Other"
]

STATUSES = [
    "Pending",
    "In Progress",
    "Resolved"
]

PRIORITIES = [
    "Low",
    "Medium",
    "High"
]

BUILDINGS = [
    "Block A",
    "Block B",
    "Block C",
    "Computer Lab",
    "Library",
    "Hostel Block"
]

DEPARTMENTS = [
    "CSE",
    "CSE (AI)",
    "ECE",
    "BCA",
    "BBA",
    "MBA",
    "Other"
]


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    """
    Create and return a SQLite database connection.
    """

    os.makedirs(DATA_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():

    conn = get_db()

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            complaint_id TEXT UNIQUE NOT NULL,

            student_name TEXT NOT NULL,

            department TEXT NOT NULL,

            building TEXT NOT NULL,

            room_no TEXT NOT NULL,

            category TEXT NOT NULL,

            problem TEXT NOT NULL,

            priority TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Pending',

            date TEXT NOT NULL
        );


        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            complaint_id TEXT NOT NULL,

            staff_name TEXT NOT NULL,

            repair_date TEXT NOT NULL,

            cost REAL NOT NULL DEFAULT 0,

            remarks TEXT,

            FOREIGN KEY (complaint_id)
            REFERENCES complaints(complaint_id)
        );
        """
    )

    conn.commit()

    # Add sample data only when database is empty
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM complaints"
    ).fetchone()["c"]

    if count == 0:
        seed_sample_data(conn)

    conn.close()


# ============================================================
# SAMPLE DATA
# ============================================================

def seed_sample_data(conn):

    sample = [

        (
            "Rahul Sharma",
            "CSE (AI)",
            "Block A",
            "204",
            "Electrical",
            "Fan not working",
            "Medium",
            "Pending",
            "2026-03-04"
        ),

        (
            "Aman Verma",
            "BCA",
            "Block B",
            "112",
            "Furniture",
            "Broken classroom chair",
            "Low",
            "Resolved",
            "2026-03-06"
        ),

        (
            "Neha Singh",
            "CSE",
            "Computer Lab",
            "CL-02",
            "IT",
            "Projector not displaying",
            "High",
            "In Progress",
            "2026-03-10"
        ),

        (
            "Riya Patel",
            "ECE",
            "Block C",
            "118",
            "Plumbing",
            "Tap leakage",
            "High",
            "Resolved",
            "2026-03-12"
        ),

        (
            "Arjun Mehta",
            "CSE (AI)",
            "Block A",
            "305",
            "Internet",
            "Wi-Fi connection unstable",
            "Medium",
            "Pending",
            "2026-03-15"
        ),

        (
            "Priya Rao",
            "BBA",
            "Library",
            "L-01",
            "Cleaning",
            "Reading area needs cleaning",
            "Low",
            "Resolved",
            "2026-03-18"
        ),

        (
            "Vikram Das",
            "ECE",
            "Hostel Block",
            "H-21",
            "AC/Cooling",
            "Cooler not working",
            "High",
            "In Progress",
            "2026-03-22"
        ),

        (
            "Kiran Joshi",
            "CSE",
            "Block B",
            "210",
            "Electrical",
            "Tube light flickering",
            "Medium",
            "Pending",
            "2026-03-25"
        ),

        (
            "Sahil Khan",
            "CSE (AI)",
            "Block A",
            "118",
            "Furniture",
            "Desk drawer damaged",
            "Low",
            "Resolved",
            "2026-03-28"
        ),

        (
            "Megha Nair",
            "BCA",
            "Computer Lab",
            "CL-05",
            "IT",
            "Keyboard not working",
            "Medium",
            "Resolved",
            "2026-04-01"
        ),

        (
            "Dev Kumar",
            "ECE",
            "Block C",
            "220",
            "Internet",
            "Network port inactive",
            "High",
            "In Progress",
            "2026-04-04"
        ),

        (
            "Anjali Shah",
            "BBA",
            "Library",
            "L-08",
            "Electrical",
            "Study lamp not working",
            "Low",
            "Resolved",
            "2026-04-08"
        ),

        (
            "Rohan Gupta",
            "CSE",
            "Block A",
            "401",
            "Plumbing",
            "Washbasin leakage",
            "High",
            "Pending",
            "2026-04-12"
        ),

        (
            "Pooja Yadav",
            "CSE (AI)",
            "Hostel Block",
            "H-08",
            "Cleaning",
            "Room corridor cleaning",
            "Low",
            "Resolved",
            "2026-04-15"
        ),

        (
            "Nitin Roy",
            "ECE",
            "Block B",
            "106",
            "AC/Cooling",
            "Fan speed very low",
            "Medium",
            "Pending",
            "2026-04-18"
        ),

        (
            "Isha Jain",
            "BCA",
            "Block C",
            "101",
            "Other",
            "Door lock needs repair",
            "Medium",
            "Resolved",
            "2026-04-21"
        ),

        (
            "Aditya Sen",
            "CSE",
            "Computer Lab",
            "CL-01",
            "IT",
            "CPU not starting",
            "High",
            "In Progress",
            "2026-04-25"
        ),

        (
            "Simran Kaur",
            "BBA",
            "Library",
            "L-04",
            "Internet",
            "Wi-Fi down",
            "High",
            "Resolved",
            "2026-04-28"
        ),

        (
            "Harsh Patel",
            "CSE (AI)",
            "Block A",
            "212",
            "Electrical",
            "Switchboard loose",
            "Medium",
            "Pending",
            "2026-05-02"
        ),

        (
            "Nisha Verma",
            "ECE",
            "Block B",
            "203",
            "Furniture",
            "Broken bench",
            "Low",
            "Resolved",
            "2026-05-05"
        )
    ]

    for index, row in enumerate(sample, start=1):

        complaint_id = f"CMP{index:03d}"

        conn.execute(
            """
            INSERT INTO complaints
            (
                complaint_id,
                student_name,
                department,
                building,
                room_no,
                category,
                problem,
                priority,
                status,
                date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                complaint_id,
                *row
            )
        )

    conn.commit()


# ============================================================
# ADMIN DECORATOR
# ============================================================

def admin_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("admin_logged_in"):

            flash(
                "Admin login is required for this action.",
                "error"
            )

            return redirect(
                url_for("admin_login")
            )

        return view(*args, **kwargs)

    return wrapped


# ============================================================
# GET SINGLE COMPLAINT
# ============================================================

def get_complaint(complaint_id):

    conn = get_db()

    complaint_id = complaint_id.upper().strip()

    row = conn.execute(
        """
        SELECT *
        FROM complaints
        WHERE complaint_id = ?
        """,
        (complaint_id,)
    ).fetchone()

    conn.close()

    return row


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) AS c FROM complaints"
    ).fetchone()["c"]

    pending = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM complaints
        WHERE status = 'Pending'
        """
    ).fetchone()["c"]

    progress = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM complaints
        WHERE status = 'In Progress'
        """
    ).fetchone()["c"]

    resolved = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM complaints
        WHERE status = 'Resolved'
        """
    ).fetchone()["c"]

    common = conn.execute(
        """
        SELECT category, COUNT(*) AS c
        FROM complaints
        GROUP BY category
        ORDER BY c DESC
        LIMIT 1
        """
    ).fetchone()

    building = conn.execute(
        """
        SELECT building, COUNT(*) AS c
        FROM complaints
        GROUP BY building
        ORDER BY c DESC
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    return render_template(
        "dashboard.html",

        total=total,

        pending=pending,

        progress=progress,

        resolved=resolved,

        common=(
            common["category"]
            if common
            else "—"
        ),

        building=(
            building["building"]
            if building
            else "—"
        )
    )


# ============================================================
# STUDENT PORTAL
# ============================================================

@app.route("/student")
def student_portal():

    return render_template(
        "student_portal.html"
    )


# ============================================================
# STUDENT TRACK COMPLAINT
# ============================================================

@app.route(
    "/student/track",
    methods=["GET", "POST"]
)
def student_track():

    complaint = None

    maintenance = []

    if request.method == "POST":

        complaint_id = request.form.get(
            "complaint_id",
            ""
        ).strip().upper()

        student_name = request.form.get(
            "student_name",
            ""
        ).strip()

        if not complaint_id or not student_name:

            flash(
                "Please enter Complaint ID and Student Name.",
                "error"
            )

            return render_template(
                "student_portal.html"
            )

        conn = get_db()

        complaint = conn.execute(
            """
            SELECT *
            FROM complaints
            WHERE complaint_id = ?
            AND LOWER(student_name) = LOWER(?)
            """,
            (
                complaint_id,
                student_name
            )
        ).fetchone()

        if complaint:

            maintenance = conn.execute(
                """
                SELECT *
                FROM maintenance
                WHERE complaint_id = ?
                ORDER BY id DESC
                """,
                (complaint_id,)
            ).fetchall()

        conn.close()

        if not complaint:

            flash(
                "Complaint ID or Student Name is incorrect.",
                "error"
            )

            return render_template(
                "student_portal.html"
            )

    return render_template(
        "student_track.html",
        complaint=complaint,
        maintenance=maintenance
    )


# ============================================================
# REGISTER COMPLAINT
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        data = {
            "student_name": request.form.get(
                "student_name",
                ""
            ).strip(),

            "department": request.form.get(
                "department",
                ""
            ).strip(),

            "building": request.form.get(
                "building",
                ""
            ).strip(),

            "room_no": request.form.get(
                "room_no",
                ""
            ).strip(),

            "category": request.form.get(
                "category",
                ""
            ).strip(),

            "priority": request.form.get(
                "priority",
                ""
            ).strip(),

            "problem": request.form.get(
                "problem",
                ""
            ).strip()
        }

        required = [
            "student_name",
            "department",
            "building",
            "room_no",
            "category",
            "priority",
            "problem"
        ]

        # Validate form
        for field in required:

            if not data[field]:

                flash(
                    "Please fill in all required fields.",
                    "error"
                )

                return render_template(
                    "register.html",
                    **data
                )

        conn = get_db()

        try:

            # Generate new ID safely
            last_id = conn.execute(
                """
                SELECT id
                FROM complaints
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()

            if last_id:

                next_id = last_id["id"] + 1

            else:

                next_id = 1

            complaint_id = f"CMP{next_id:03d}"

            conn.execute(
                """
                INSERT INTO complaints
                (
                    complaint_id,
                    student_name,
                    department,
                    building,
                    room_no,
                    category,
                    problem,
                    priority,
                    status,
                    date
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    'Pending',
                    ?
                )
                """,
                (
                    complaint_id,
                    data["student_name"],
                    data["department"],
                    data["building"],
                    data["room_no"],
                    data["category"],
                    data["problem"],
                    data["priority"],
                    date.today().isoformat()
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.rollback()
            conn.close()

            flash(
                "Could not create the complaint ID. Please try again.",
                "error"
            )

            return render_template(
                "register.html",
                **data
            )

        except Exception as e:

            conn.rollback()
            conn.close()

            flash(
                f"Error while registering complaint: {e}",
                "error"
            )

            return render_template(
                "register.html",
                **data
            )

        conn.close()

        return render_template(
            "success.html",
            complaint_id=complaint_id
        )

    return render_template(
        "register.html"
    )


# ============================================================
# VIEW / SEARCH COMPLAINTS
# ============================================================

@app.route("/tickets")
def tickets():

    q = request.args.get(
        "q",
        ""
    ).strip()

    conn = get_db()

    if q:

        rows = conn.execute(
            """
            SELECT *
            FROM complaints

            WHERE complaint_id LIKE ?
            OR student_name LIKE ?
            OR category LIKE ?
            OR building LIKE ?

            ORDER BY id DESC
            """,
            (
                f"%{q}%",
                f"%{q}%",
                f"%{q}%",
                f"%{q}%"
            )
        ).fetchall()

    else:

        rows = conn.execute(
            """
            SELECT *
            FROM complaints
            ORDER BY id DESC
            """
        ).fetchall()

    conn.close()

    return render_template(
        "tickets.html",
        tickets=rows,
        q=q
    )


# ============================================================
# COMPLAINT DETAILS
# ============================================================

@app.route(
    "/ticket/<complaint_id>"
)
def ticket_detail(complaint_id):

    complaint = get_complaint(
        complaint_id
    )

    if not complaint:

        flash(
            "Complaint Not Found.",
            "error"
        )

        return redirect(
            url_for("tickets")
        )

    conn = get_db()

    maintenance = conn.execute(
        """
        SELECT *
        FROM maintenance
        WHERE complaint_id = ?
        ORDER BY id DESC
        """,
        (
            complaint_id.upper(),
        )
    ).fetchall()

    conn.close()

    return render_template(
        "ticket_detail.html",
        complaint=complaint,
        maintenance=maintenance
    )

# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            session["admin_username"] = username

            flash("Admin login successful.", "success")
            return redirect(url_for("admin_panel"))

        flash("Invalid admin username or password.", "error")

    return render_template("admin_login.html")