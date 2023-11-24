from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
import models
import schemas, crud_paciente

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=['*'],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/")
def raiz():
	return RedirectResponse(url="/docs/")        

#### Pacientes

@app.post("/pacientes/", response_model=schemas.Paciente)
def create_paciente(paciente: schemas.PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = crud_paciente.create_paciente(db=db, paciente=paciente)
    return db_paciente


@app.get("/pacientes/", response_model=list[schemas.Paciente])
def get_pacientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pacientes = crud_paciente.get_pacientes(db, skip=skip, limit=limit)
    return pacientes


@app.get("/pacientes/{id_paciente}", response_model=schemas.Paciente)
def get_paciente(id_paciente: int, db: Session = Depends(get_db)):
    db_paciente = crud_paciente.get_paciente_by_id(db, id_paciente=id_paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    return db_paciente


@app.put("/pacientes/{id_paciente}", response_model=schemas.Paciente)
def update_paciente(
    id_paciente: int, paciente_update: schemas.PacienteUpdate, db: Session = Depends(get_db)
):
    db_paciente = crud_paciente.get_paciente_by_id(db, id_paciente=id_paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    db_paciente = crud_paciente.update_paciente(db, db_paciente, paciente_update)
    return db_paciente


@app.delete("/pacientes/{id_paciente}", response_model=schemas.Paciente)
def delete_paciente(id_paciente: int, db: Session = Depends(get_db)):
    db_paciente = crud_paciente.get_paciente_by_id(db, id_paciente=id_paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="El ID del paciente no existe")
    crud_paciente.delete_paciente(db, db_paciente)
    return db_paciente


#### Expedientes    

