from sqlalchemy.orm import Session
import models
import schemas, models
  
def create_paciente(db: Session, paciente: schemas.PacienteCreate):
        db_paciente = models.Paciente(**paciente.model_dump())
        db.add(db_paciente)
        db.commit()
        db.refresh(db_paciente)
        return (db_paciente)


def get_paciente_by_id(db: Session, id_paciente: int):
    return db.query(models.Paciente).filter(models.Paciente.id_paciente == id_paciente).first()


def get_pacientes(db: Session, skip = 0, limit: int = 100):
    return db.query(models.Paciente).offset(skip).limit(limit).all()


def update_paciente(db: Session, paciente: models.Paciente, paciente_update: schemas.PacienteUpdate):
    for key, value in paciente_update.dict().items():
        setattr(paciente, key, value)
    db.commit()
    db.refresh(paciente)
    return paciente


def delete_paciente(db: Session, paciente: models.Paciente):
    db.delete(paciente)
    db.commit()
