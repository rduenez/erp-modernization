mkdir erp-migrations
cd erp-migrations
python -m venv venv

# Activate the virtual environment (Windows)
.\venv\Scripts\activate

# Install SQLAlchemy (ORM), Alembic (Migrations), and Psycopg2 (Postgres driver)
pip install sqlalchemy alembic psycopg2-binary
