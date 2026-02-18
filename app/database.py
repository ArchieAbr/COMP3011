import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()  # Load local .env when running outside Azure

raw_url = os.getenv("DATABASE_URL")
if not raw_url:
    raise RuntimeError("DATABASE_URL is not set; configure it as an app setting or secret.")

normalized_url = raw_url.replace("postgres://", "postgresql://", 1) if raw_url.startswith("postgres://") else raw_url
database_url = make_url(normalized_url)

connect_args = {}
if database_url.get_backend_name() == "postgresql":
    connect_args["sslmode"] = os.getenv("DB_SSLMODE", "require")

engine = create_engine(database_url, echo=True, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()