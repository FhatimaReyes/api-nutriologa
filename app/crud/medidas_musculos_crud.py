from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import MedidasMusculosCreate, MedidasMusculosUpdate
from models.models import MedidasMusculos as models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_medidas_musculos(db: Session, medidas_musculos: MedidasMusculosCreate):
    db_medidas_musculos = models(**medidas_musculos.model_dump())
    db.add(db_medidas_musculos)
    db.commit()
    db.refresh(db_medidas_musculos)
    return db_medidas_musculos

def get_medidas_musculos_by_id(db: Session, id_musculos: int):
    return db.query(models).filter(models.id_musculos == id_musculos).first()
    
def get_medidas_musculos(db: Session, skip=0, limit: int = 100):
    return db.query(models).offset(skip).limit(limit).all()

def update_medidas_musculos(db: Session, medidas_musculos: models, medidas_musculos_update: MedidasMusculosUpdate):
    for key, value in medidas_musculos_update.dict().items():
        setattr(medidas_musculos, key, value)
    db.commit()
    db.refresh(medidas_musculos)
    return medidas_musculos

def delete_medidas_musculos(db: Session, medidas_musculos: models):
    db.delete(medidas_musculos)
    db.commit()
