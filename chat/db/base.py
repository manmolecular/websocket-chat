from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import database_exists, create_database

from chat.utils.config import DbValues

# Create engine to connect to PostgreSQL, psycopg2 driver is required though
Engine = create_engine(
    f"postgres+psycopg2://"
    f"{DbValues.POSTGRES_USER}:{DbValues.POSTGRES_PASSWORD}@"
    f"{DbValues.POSTGRES_HOST}:{DbValues.POSTGRES_PORT}/"
    f"{DbValues.POSTGRES_DATABASE}",
    poolclass=NullPool,
)

# Create database if not exists yet
if not database_exists(Engine.url):
    create_database(Engine.url)

# Define local session and base to use
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()
