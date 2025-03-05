# database.py - MySQL Database connection setup

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/image_processor")

# Create engine with connection pooling
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model for ORM
Base = declarative_base()
