from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import MedidasHuesos, MedidasHuesosCreate, MedidasHuesosUpdate
from crud.medidas_huesos_crud import create_medidas_huesos, get_medidas_huesos, get_medidas_huesos_by_id, update_medidas_huesos, delete_medidas_huesos, get_medidas_huesos_by_id_paciente
from crud.paciente_crud import get_paciente_by_id

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/medidas_huesos/", response_model=MedidasHuesos)
def agregar_medidas_huesos(medidas_huesos: MedidasHuesosCreate, db: Session = Depends(get_db)):
    paciente = get_paciente_by_id(db, id_paciente=medidas_huesos.id_paciente)
    if paciente is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    db_medida_hueso = create_medidas_huesos(db=db, medidas_huesos=medidas_huesos)
    return db_medida_hueso

@router.get("/medidas_huesos/", response_model=list[MedidasHuesos])
def obtener_medidas_huesos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    medidas_huesos = get_medidas_huesos(db, skip=skip, limit=limit)
    return medidas_huesos

@router.get("/medidas_huesos/{id_huesos}", response_model=MedidasHuesos)
def obtener_medidas_huesos_por_id(id_huesos: int, db: Session = Depends(get_db)):
    db_medida_hueso = get_medidas_huesos_by_id(db, id_huesos=id_huesos)
    if db_medida_hueso is None:
        raise HTTPException(status_code=404, detail="El ID de las medidas de hueso no existe")
    return db_medida_hueso

@router.get("/medidas_huesos/paciente/{id_paciente}", response_model=list[MedidasHuesos])
def obtener_medidas_huesos_por_id_paciente(id_paciente: int, db: Session = Depends(get_db)):
    db_medida_hueso = get_medidas_huesos_by_id_paciente(db, id_paciente=id_paciente)
    if db_medida_hueso is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    return db_medida_hueso

@router.put("/medidas_huesos/{id_huesos}", response_model=MedidasHuesos)
def actualizar_medidas_huesos(
    id_medida_hueso: int, medida_hueso_update: MedidasHuesosUpdate, db: Session = Depends(get_db)
):
    db_medida_hueso = get_medidas_huesos_by_id(db, id_huesos=id_medida_hueso)
    if db_medida_hueso is None:
        raise HTTPException(status_code=404, detail="El ID de la medida del hueso no existe")
    db_medida_hueso = update_medidas_huesos(db, db_medida_hueso, medida_hueso_update)
    return db_medida_hueso

@router.delete("/medidas_huesos/{id_huesos}", response_model=MedidasHuesos)
def eliminar_medidas_huesos(id_huesos: int, db: Session = Depends(get_db)):
    db_medida_hueso = get_medidas_huesos_by_id(db, id_huesos=id_huesos)
    if db_medida_hueso is None:
        raise HTTPException(status_code=404, detail="El ID de las medidas de huesos no existe")
    delete_medidas_huesos(db, db_medida_hueso)
    return db_medida_hueso
