import os

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

# PUBLIC_INTERFACE
class Command(BaseCommand):
    """
    Ensures that the configured PostgreSQL database exists.

    WARNING: This logic is ONLY executed as an explicit management command!
    Database socket, psycopg and DNS checks are never run at import/startup,
    only when this command is explicitly invoked.
    """

    help = "Ensures that the configured PostgreSQL database exists, creating it if necessary."

    def handle(self, *args, **options):
        import psycopg
        import time
        import socket

        db_name = (
            os.getenv("DB_NAME")
            or os.getenv("POSTGRES_DB")
            or "notes_db"
        )
        db_user = (
            os.getenv("DB_USER")
            or os.getenv("POSTGRES_USER")
            or "postgres"
        )
        db_password = (
            os.getenv("DB_PASSWORD")
            or os.getenv("POSTGRES_PASSWORD")
            or "postgres"
        )
        db_host = (
            os.getenv("DB_HOST")
            or os.getenv("POSTGRES_HOST")
            or "database"
        )
        db_port = (
            os.getenv("DB_PORT")
            or os.getenv("POSTGRES_PORT")
            or "5001"
        )
        # Allow DATABASE_URL override
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Parse manually for psycopg connection (urlparse)
            from urllib.parse import urlparse
            url = urlparse(database_url)
            db_name = url.path.lstrip("/") if url.path and url.path != "/" else db_name
            db_user = url.username or db_user
            db_password = url.password or db_password
            # Always ensure fallback to 'database' and 5001, never localhost/5000
            db_host = url.hostname if url.hostname else "database"
            db_port = str(url.port) if url.port else "5001"

        target_conninfo = f"host={db_host} port={db_port} dbname={db_name} user={db_user} password={db_password}"

        # This check is only done in this command (never at import), and will NOT stop migrations, only warn and exit early.
        try:
            socket.gethostbyname(db_host)
        except Exception as dns_exc:
            self.stdout.write(
                self.style.WARNING(
                    f"Database hostname '{db_host}' could not be resolved: {dns_exc}. "
                    "Skipping database existence check/creation. Ensure the database is available before running migrations."
                )
            )
            return

        # Try connect to target DB, if success do nothing
        try:
            with psycopg.connect(target_conninfo, autocommit=True, connect_timeout=2):
                self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' already exists and is reachable."))
                return
        except OperationalError as exc:
            # If DB does not exist, connect to postgres and create it
            if "does not exist" not in str(exc):
                self.stdout.write(self.style.WARNING(f"Could not connect to '{db_name}': {exc}"))
                # Also try to connect to system DB and check if the DB exists
            self.stdout.write(f"Database '{db_name}' not found, will attempt creation...")

        # Try to create DB via 'postgres' or fallback to 'template1'
        admin_db = "postgres"
        for system_db in (admin_db, "template1"):
            admin_conninfo = f"host={db_host} port={db_port} dbname={system_db} user={db_user} password={db_password}"
            for attempt in range(5):
                try:
                    with psycopg.connect(admin_conninfo, autocommit=True, connect_timeout=2) as admin_conn:
                        try:
                            with admin_conn.cursor() as cur:
                                cur.execute(f"CREATE DATABASE \"{db_name}\"")
                                self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' created via '{system_db}'."))
                                return
                        except psycopg.errors.DuplicateDatabase:
                            self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' already exists (race)."))
                            return
                        except Exception as dbexc:
                            # Might be another error (insufficient privilege, etc)
                            self.stdout.write(self.style.ERROR(f"Failed to create DB: {dbexc}"))
                            raise dbexc
                except OperationalError as conn_exc:
                    if attempt < 4:
                        time.sleep(2)
                        continue
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Cannot connect to admin DB '{system_db}' ({conn_exc}). "
                                "If database is not available yet, run this command again later."
                            )
                        )
            # Try next system DB
        self.stdout.write(self.style.ERROR(f"Exhausted all admin DBs. Could not connect to create database '{db_name}'."))
        # Do not sys.exit(1); just warn but allow migration or manage.py to continue.
