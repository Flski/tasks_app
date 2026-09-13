from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import database_file_path


engine = create_engine(database_file_path, connect_args={"check_same_thread": False})

db_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

DB = declarative_base()