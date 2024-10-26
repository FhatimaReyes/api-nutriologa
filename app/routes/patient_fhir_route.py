from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from crud.paciente_crud import get_paciente_by_id
from schemas.schemas import FhirPatientCreate
from fastapi import HTTPException
from fhir.resources.bundle import Bundle
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
        # Registro de depuración para verificar los datos de db_paciente
        #print(f"Datos del paciente: {db_paciente}")
        genero_parsed = {
            'M': 'male',
            'F': 'female',
        }
        
        gender = genero_parsed.get(db_paciente.genero, 'unknown')
        
        # Construir el recurso Patient
        paciente = Patient.construct(
            id=str(db_paciente.id_paciente),
            name=[HumanName.construct(given=[db_paciente.nombre])],
            telecom=(
                [ContactPoint.construct(system="phone", value=db_paciente.telefono, use="mobile")]
                if db_paciente.telefono
                else None
            ),
            birthDate=str(db_paciente.fecha_nacimiento) if db_paciente.fecha_nacimiento else None,
            gender=gender,
            extension=(
                [{"url": "http://example.org/fhir/StructureDefinition/occupation", "valueString": db_paciente.ocupacion}]
                if db_paciente.ocupacion
                else None
            ),
        )

        # Registro de depuración para verificar el objeto Patient
        #print(f"Recurso Patient: {paciente.json(indent=2)}")

        # Crear el Bundle FHIR de tipo transaction
        bundle = Bundle.construct(
            type="transaction",
            entry=[
                {
                    "resource": paciente,
                    "request": {"method": "POST", "url": "Patient"}
                }
            ]
        )
        # Registro de depuración para verificar el objeto Bundle
        #print(f"Recurso Bundle: {bundle.json(indent=2)}")

        # Convertir el Bundle a JSON
        bundle_json = bundle.json()

        # Enviar el Bundle al servidor HAPI FHIR
        response = requests.post(
            "http://localhost:8080/fhir",  # URL de tu servidor HAPI FHIR
            headers={"Content-Type": "application/fhir+json"},
            data=bundle_json
        )

        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return {"message": "Patient creado en el servidor exitosamente"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error al crear Patient: " + str(e))

@router.get("/patient/")
def obtener_pacientes_fhir():
    try:
        # Realizar una solicitud GET al servidor HAPI FHIR
        response = requests.get("http://localhost:8080/fhir/Patient/", headers={"Accept": "application/fhir+json"})
        
        # Verificar el estado de la respuesta
        if response.status_code == 200:
            # Parsear la respuesta JSON a un objeto Python
            data = response.json()
            
            # Verificar que la estructura es la esperada
            if data.get("resourceType") == "Bundle" and "entry" in data:
                return data
            else:
                raise HTTPException(status_code=500, detail="Estructura de respuesta inesperada")
        else:
            # Si el servidor FHIR devolvió un error, lanzar una excepción HTTP
            raise HTTPException(status_code=response.status_code, detail=response.text)
    
    except requests.exceptions.RequestException as e:
        # Manejar errores de solicitud (por ejemplo, el servidor está caído)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/patient/{id}", response_model=dict)
def obtener_paciente_fhir_por_id(id: str):
    try:
        # Realizar la solicitud GET al servidor FHIR para obtener el paciente por su ID
        response = requests.get(f"http://localhost:8080/fhir/Patient/{id}")
        
        # Verificar si la solicitud fue exitosa (código de estado 200)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")        
        patient = response.json()  # Convertir la respuesta JSON a un diccionario de Python
        return patient

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con el servidor FHIR: {str(e)}")    

#@router.delete("/patient/{id}", response_model=dict)
#def eliminar_paciente_fhir(id: str):
#        response = requests.delete(f"http://localhost:8080/fhir/Patient/{id}", headers={"Accept": "application/fhir+json"})
#        
#        if response.status_code != 204:
#            raise HTTPException(status_code=response.status_code)
#        return {"message": "Paciente eliminado exitosamente"}
    

@router.delete("/patient/{patient_id}", response_model=dict)
def delete_patient_and_related_resources(patient_id: str):
    try:
        # Verificar si el paciente existe antes de intentar eliminarlo
        patient_response = requests.get(f"http://localhost:8080/fhir/Patient/{patient_id}")
        if patient_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        # Eliminar Observations relacionadas con el Patient
        observations_response = requests.get(f"http://localhost:8080/fhir/Observation?patient=Patient/{patient_id}")
        observations = observations_response.json().get('entry', [])
        for observation in observations:
            observation_id = observation['resource']['id']
            delete_observation_response = requests.delete(f"http://localhost:8080/fhir/Observation/{observation_id}")
            if delete_observation_response.status_code != 204:
                raise HTTPException(status_code=delete_observation_response.status_code, detail=f"Error al eliminar la observación {observation_id}")

        # Eliminar el Patient después de las Observations
        delete_patient_response = requests.delete(f"http://localhost:8080/fhir/Patient/{patient_id}")
        if delete_patient_response.status_code != 204:
            raise HTTPException(status_code=delete_patient_response.status_code, detail="Error al eliminar el paciente")

        return {"message": "Paciente y Observations relacionadas eliminadas exitosamente"}

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con el servidor FHIR: {str(e)}")
    except HTTPException as he:
        raise he