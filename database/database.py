from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from config import DB_HOST, DB_USER, DB_NAME, DB_PASSWORD, DB_PORT

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
Session = sessionmaker(engine, autocommit=False, autoflush=False)

Base = declarative_base()


def create_db():
    logger.info("Creating database tables")
    Base.metadata.create_all(engine)