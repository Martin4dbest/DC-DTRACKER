import logging
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool
from flask import current_app

# Import Flask app and db
from app import app, db

# Import your models so Alembic can detect them
import models  # Ensure all models are imported here

# Alembic Configuration
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Set the database URL dynamically from Flask's app config
config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

# Set target_metadata to db.metadata
target_metadata = db.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(config.get_main_option('sqlalchemy.url'))

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
