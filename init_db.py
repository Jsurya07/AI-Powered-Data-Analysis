# init_db.py

from models import Base, QueryLog  # Import all models here
from db import engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created.")
