from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from schemas.schemas import MedidasMusculos, MedidasMusculosCreate, MedidasMusculosUpdate
from crud.medidas_musculos_crud import create_medidas_musculos, get_medidas_musculos, get_medidas_musculos_by_id, update_medidas_musculos, delete_medidas_musculos

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/medidas_musculos/", response_model=MedidasMusculos)
def agregar_medidas_musculos(medidas_musculos: MedidasMusculosCreate, db: Session = Depends(get_db)):
    db_medida_musculo = create_medidas_musculos(db=db, medidas_musculos=medidas_musculos)
    return db_medida_musculo

@router.get("/medidas_musculos/", response_model=list[MedidasMusculos])
def obtener_medidas_musculos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    medidas_musculos = get_medidas_musculos(db, skip=skip, limit=limit)
    return medidas_musculos

@router.get("/medidas_musculos/{id_musculos}", response_model=MedidasMusculos)
def obtener_medidas_musculos_por_id(id_musculos: int, db: Session = Depends(get_db)):
    db_medida_musculo = get_medidas_musculos_by_id(db, id_musculos=id_musculos)
    if db_medida_musculo is None:
        raise HTTPException(status_code=404, detail="El ID de las medidas de músculo no existe")
    return db_medida_musculo

@router.put("/medidas_musculos/{id_musculos}", response_model=MedidasMusculos)
def actualizar_medidas_musculos(
    id_medida_musculo: int, medida_musculo_update: MedidasMusculosUpdate, db: Session = Depends(get_db)
):
    db_medida_musculo = get_medidas_musculos_by_id(db, id_musculos=id_medida_musculo)
    if db_medida_musculo is None:
        raise HTTPException(status_code=404, detail="El ID de la medida del músculo no existe")
    db_medida_musculo = update_medidas_musculos(db, db_medida_musculo, medida_musculo_update)
    return db_medida_musculo

@router.delete("/medidas_musculos/{id_musculos}", response_model=MedidasMusculos)
def eliminar_medidas_musculos(id_musculos: int, db: Session = Depends(get_db)):
    db_medida_musculo = get_medidas_musculos_by_id(db, id_musculos=id_musculos)
    if db_medida_musculo is None:
        raise HTTPException(status_code=404, detail="El ID de las medidas de músculos no existe")
    delete_medidas_musculos(db, db_medida_musculo)
    return db_medida_musculo
