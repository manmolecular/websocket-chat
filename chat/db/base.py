from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import database_exists, create_database

from chat.utils.config import DbValues

Engine = create_engine(
    f"postgres+psycopg2://"
    f"{DbValues.POSTGRES_USER}:{DbValues.POSTGRES_PASSWORD}@"
    f"{DbValues.POSTGRES_HOST}:{DbValues.POSTGRES_PORT}/"
    f"{DbValues.POSTGRES_DATABASE}",
    poolclass=NullPool,
)
if not database_exists(Engine.url):
    create_database(Engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()
