from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import ConsultaCreate, ConsultaUpdate
from models.models import Consulta as models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_consulta(db: Session, consulta: ConsultaCreate):
    db_consulta = models(**consulta.model_dump())
    db.add(db_consulta)
    db.commit()
    db.refresh(db_consulta)
    return db_consulta

def get_consulta_by_id(db: Session, id_consulta: int):
    return db.query(models).filter(models.id_consulta == id_consulta).first()

def get_consultas(db: Session, skip=0, limit: int = 100):
    return db.query(models).offset(skip).limit(limit).all()

def update_consulta(db: Session, consulta: models, consulta_update: ConsultaUpdate):
    for key, value in consulta_update.dict().items():
        setattr(consulta, key, value)
    db.commit()
    db.refresh(consulta)
    return consulta

def delete_consulta(db: Session, consulta: models):
    db.delete(consulta)
    db.commit()
