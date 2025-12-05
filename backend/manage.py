#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
        import subprocess

        # If migration, makemigrations or migrate is one of the commands,
        # ensure the DB exists by running 'ensure_db'.
        manage_args = sys.argv[1:]
        ensure_db_before = {"migrate", "makemigrations", "createsuperuser", "collectstatic"}
        if manage_args and manage_args[0] in ensure_db_before:
            subprocess.run([sys.executable, os.path.abspath(__file__), "ensure_db"], check=True)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
