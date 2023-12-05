from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:CG--fG5f6a5-36a*5agFE3AGeGfEFD-2@roundhouse.proxy.rlwy.net:22059/railway"
#DATABASE_URL = "postgresql://postgres:password@localhost:5432/nutriologa" #se usó para hacer pruebas locales

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
