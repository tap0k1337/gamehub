# GameHub

This project is a simple marketplace for digital goods built with Flask and SQLAlchemy.

## Database setup

After cloning the repository, create the SQLite database using the `init_db.py` script:

```bash
python init_db.py
```

Running this script will remove any existing `instance/gamehub.db` file and create a fresh database with all tables.

If you already had a previous version of the database, be aware that it will be deleted when running the script. Back up any important data before executing it.
