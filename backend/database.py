import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# PostgreSQL connection string — reads from environment variable if present
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:12345678@localhost:5433/sioradb"
)

# Engine = the actual connection to the database.
# Every database operation goes through this.
engine = create_engine(DATABASE_URL)

# SessionLocal = a "session factory".
# Each time we need to talk to the database, we create a new session from this.
# autocommit=False → we manually commit transactions (safer, gives us control)
# autoflush=False  → SQLAlchemy won't issue intermediate SQL automatically
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = the parent class for all our models (Conversation, Message, etc.)
# Every model class inherits from Base — that's how SQLAlchemy knows
# the class represents a database table.
Base = declarative_base()

def get_db():
    # Create a fresh database session for each incoming API request.
    db = SessionLocal()
    try:
        yield db  # hand the session to the request handler
    finally:
        db.close()  # always close the session after the request finishes (frees the connection)
