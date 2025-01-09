from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from config import settings
from sqlalchemy_utils import database_exists, create_database

from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)

Base = declarative_base()

if not database_exists(settings.DATABASE_URL):
        create_database(settings.DATABASE_URL)

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

Session = sessionmaker(bind=engine)

logger.info(f"Database connection established: {settings.DATABASE_URL}")

def get_session():
    session = Session()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()