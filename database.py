
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).parent / "college_lab.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
                CHECK (role IN ('student', 'admin'))
        );

        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            equipment_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK (status IN (
                    'Pending', 'Approved', 'Rejected',
                    'Returned', 'Cancelled'
                )),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (equipment_id) REFERENCES equipment(id),
            CHECK (start_time < end_time)
        );
    """)

    count = connection.execute(
        "SELECT COUNT(*) FROM equipment"
    ).fetchone()[0]

    if count == 0:
        equipment_items = [
            (
                "Arduino Kit",
                "Electronics",
                "Development kit for embedded systems."
            ),
            (
                "Raspberry Pi",
                "Computing",
                "Compact computer for programming and IoT."
            ),
            (
                "Robotics Kit",
                "Robotics",
                "Kit for robotics and automation experiments."
            ),
            (
                "Digital Multimeter",
                "Electronics",
                "Device for measuring electrical quantities."
            ),
            (
                "IoT Sensor Kit",
                "Internet of Things",
                "Sensors for IoT experiments."
            ),
            (
                "3D Printer",
                "Manufacturing",
                "Equipment for prototype manufacturing."
            )
        ]

        connection.executemany("""
            INSERT INTO equipment (name, category, description)
            VALUES (?, ?, ?)
        """, equipment_items)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DATABASE}")
