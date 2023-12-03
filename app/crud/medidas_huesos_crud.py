
from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import MedidasHuesosCreate, MedidasHuesosUpdate
from models.models import MedidasHuesos as models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_medidas_huesos(db: Session, medidas_huesos: MedidasHuesosCreate):
    db_medidas_huesos = models(**medidas_huesos.model_dump())
    db.add(db_medidas_huesos)
    db.commit()
    db.refresh(db_medidas_huesos)
    return db_medidas_huesos

def get_medidas_huesos_by_id(db: Session, id_huesos: int):
    return db.query(models).filter(models.id_huesos == id_huesos).first()
    
def get_medidas_huesos(db: Session, skip=0, limit: int = 100):
    return db.query(models).offset(skip).limit(limit).all()

def update_medidas_huesos(db: Session, medidas_huesos: models, medidas_huesos_update: MedidasHuesosUpdate):
    for key, value in medidas_huesos_update.dict().items():
        setattr(medidas_huesos, key, value)
    db.commit()
    db.refresh(medidas_huesos)
    return medidas_huesos

def delete_medidas_huesos(db: Session, medidas_huesos: models):
    db.delete(medidas_huesos)
    db.commit()
