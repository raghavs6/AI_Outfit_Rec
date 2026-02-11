import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# This is the connection string for Postgres:
# format: postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/outfit"
)

# Engine = the core connection object SQLAlchemy uses to talk to the DB
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal() will create a new DB session whenever we call it
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is what all our model classes (tables) will inherit from
class Base(DeclarativeBase):
    pass