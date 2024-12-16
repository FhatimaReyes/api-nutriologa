from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from crud.paciente_crud import get_paciente_by_id
from schemas.schemas import FhirPatientCreate
from fastapi import HTTPException
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint

import requests

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/patient", response_model=dict)
def agregar_paciente_fhir(paciente: FhirPatientCreate, db: Session = Depends(get_db)):
    db_paciente = get_paciente_by_id(db, id_paciente=paciente.id_paciente)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="El paciente no existe en el sistema")
    try:
        genero_parsed = {
            'M': 'male',
            'F': 'female',
        }
        gender = genero_parsed.get(db_paciente.genero, 'unknown')
        
        # Construir el recurso Patient
        paciente_fhir = Patient.construct(
            id=str(db_paciente.id_paciente),
            name=[HumanName.construct(given=[db_paciente.nombre])],
            telecom=(
                [ContactPoint.construct(system="phone", value=db_paciente.telefono, use="mobile")]
                if db_paciente.telefono
                else None
            ),
            gender=gender,
            extension=(
                [{"url": "http://example.org/fhir/StructureDefinition/occupation", "valueString": db_paciente.ocupacion}]
                if db_paciente.ocupacion
                else None
            ),
            birthDate = db_paciente.fecha_nacimiento
        )
        
        # Convertir el recurso Patient a JSON
        paciente_json = paciente_fhir.json()

        # Enviar el recurso Patient al servidor HAPI FHIR
        response = requests.post(
            "http://localhost:8080/fhir/Patient",
            headers={"Content-Type": "application/fhir+json"},
            data=paciente_json
        )

        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return {"message": "Patient creado en el servidor"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error al crear Patient: " + str(e))
