from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import Consulta, ConsultaCreate, ConsultaUpdate
from crud.consulta_crud import create_consulta, get_consultas, get_consulta_by_id, update_consulta, delete_consulta, get_consulta_by_id_paciente

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/consultas/", response_model=Consulta)
def agregar_consulta(consulta: ConsultaCreate, db: Session = Depends(get_db)):
    db_consulta = create_consulta(db=db, consulta=consulta)
    return db_consulta

@router.get("/consultas/", response_model=list[Consulta])
def obtener_consultas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    consultas = get_consultas(db, skip=skip, limit=limit)
    return consultas

@router.get("/consultas/{id_consulta}", response_model=Consulta)
def obtener_consulta_por_id(id_consulta: int, db: Session = Depends(get_db)):
    db_consulta = get_consulta_by_id(db, id_consulta=id_consulta)
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="El ID de la consulta no existe")
    return db_consulta

@router.get("/consultas/paciente/{id_paciente}", response_model=list[Consulta])
def obtener_consulta_por_id_paciente(id_paciente: int, db: Session = Depends(get_db)):
    db_consulta = get_consulta_by_id_paciente(db, id_paciente=id_paciente)
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    return db_consulta

@router.put("/consultas/{id_consulta}", response_model=Consulta)
def actualizar_consulta(
    id_consulta: int, consulta_update: ConsultaUpdate, db: Session = Depends(get_db)
):
    db_consulta = get_consulta_by_id(db, id_consulta=id_consulta)
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="El ID de la consulta no existe")
    db_consulta = update_consulta(db, db_consulta, consulta_update)
    return db_consulta

@router.delete("/consultas/{id_consulta}", response_model=Consulta)
def eliminar_consulta(id_consulta: int, db: Session = Depends(get_db)):
    db_consulta = get_consulta_by_id(db, id_consulta=id_consulta)
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="El ID de la consulta no existe")
    delete_consulta(db, db_consulta)
    return db_consulta
