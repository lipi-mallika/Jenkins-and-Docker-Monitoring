
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# Database file location
import os

DB_PATH = Path(
    os.getenv(
        "DB_PATH",
        str(Path(__file__).with_name("monitoring.db"))
    )
)


def get_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # Jenkins build history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            build_number INTEGER NOT NULL,
            status TEXT,
            duration INTEGER,
            build_timestamp INTEGER,
            recorded_at TEXT NOT NULL,
            UNIQUE(job_name, build_number)
        )
    """)

    # Docker container status history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS container_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            container_id TEXT NOT NULL,
            container_name TEXT NOT NULL,
            status TEXT,
            health TEXT,
            recorded_at TEXT NOT NULL
        )
    """)

    # Docker CPU history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cpu_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            container_id TEXT NOT NULL,
            container_name TEXT NOT NULL,
            cpu_usage REAL,
            recorded_at TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


def save_monitoring_data(jobs, containers, cpu_data):

    connection = get_connection()

    cursor = connection.cursor()

    recorded_at = datetime.now(timezone.utc).isoformat()

    try:

        # Save Jenkins build history
        for job in jobs:

            for build in job.get("builds", []):

                build_number = build.get("number")

                if build_number is None:
                    continue

                status = (
                    "RUNNING" if build.get("building")
                    else build.get("result") or "NOT_BUILT"
                )

                cursor.execute("""
                    INSERT OR IGNORE INTO job_history
                    (
                        job_name,
                        build_number,
                        status,
                        duration,
                        build_timestamp,
                        recorded_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    job["name"],
                    build_number,
                    status,
                    build.get("duration", 0),
                    build.get("timestamp"),
                    recorded_at
                ))

        # Save Docker status only when status or health changes
        for container in containers:

            container_id = container["id"]
            container_name = container["name"]
            status = container["status"]
            health = container["health"]

            cursor.execute("""
                SELECT status, health
                FROM container_history
                WHERE container_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (container_id,))

            previous = cursor.fetchone()

            if (
                previous is None
                or previous["status"] != status
                or previous["health"] != health
            ):

                cursor.execute("""
                    INSERT INTO container_history
                    (
                        container_id,
                        container_name,
                        status,
                        health,
                        recorded_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    container_id,
                    container_name,
                    status,
                    health,
                    recorded_at
                ))

        # Save CPU readings
        for item in cpu_data:

            cursor.execute("""
                INSERT INTO cpu_history
                (
                    container_id,
                    container_name,
                    cpu_usage,
                    recorded_at
                )
                VALUES (?, ?, ?, ?)
            """, (
                item["id"],
                item["name"],
                item["cpu_usage"],
                recorded_at
            ))

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


def get_job_history():

    connection = get_connection()

    rows = connection.execute("""
        SELECT *
        FROM job_history
        ORDER BY build_timestamp DESC
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_container_history():

    connection = get_connection()

    rows = connection.execute("""
        SELECT *
        FROM container_history
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_cpu_history():

    connection = get_connection()

    rows = connection.execute("""
        SELECT *
        FROM cpu_history
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]
