from datetime import date
from pydantic import BaseModel

### Pacientes

class PacienteBase(BaseModel):
    nombre: str | None=None
    edad: int | None=None
    telefono: str | None=None
    genero: str | None=None
    fecha_nacimiento: date | None=None
    ocupacion: str | None=None
    
class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(PacienteBase):
    pass

class Paciente(PacienteBase):
    id_paciente: int | None=None
    
    class Config:
        from_attributes = True
    

### Expedientes

class ExpedienteBase(BaseModel):
    fecha_modificacion: date | None=None
    datos: str | None=None
    id_paciente: int 
    
class ExpedienteCreate(ExpedienteBase):
    pass

class ExpedienteUpdate(ExpedienteBase):
    pass

class Expediente(ExpedienteBase):
    id_expediente: int | None=None
    
    class Config:
        from_attributes = True
        
### Consultas

class ConsultaBase(BaseModel):    
    fecha: date
    pesoafuera: float
    tallaafuera: float
    tallasentado: float
    pesoadentro: float
    tallaadentro : float
    frecuencia_cardiaca : int
    nivel_oxigeno : int
    temperatura : float
    id_paciente : int
    
class ConsultaCreate(ConsultaBase):
    pass

class ConsultaUpdate(ConsultaBase):
    pass

class Consulta(ConsultaBase):
    id_consulta: int | None=None
    
    class Config:
        from_attributes = True

### Medidas_Musculos

class MedidasMusculosBase(BaseModel):
    bicep: float 
    tricep:float  
    subescapular: float
    supriliaco: float
    bicep_relajado: float
    bicep_contraido: float
    antebrazo: float
    abdomen: float
    muslo: float
    gemelo: float
    torax: float
    gluteo: float
    fecha: date
    id_paciente: int
    
class MedidasMusculosCreate(MedidasMusculosBase):
    pass

class MedidasMusculosUpdate(MedidasMusculosBase):
    pass

class MedidasMusculos(MedidasMusculosBase):
    id_musculos: int | None=None
    
    class Config:
        from_attributes = True
    
    
### Medidas_Huesos

class MedidasHuesosBase(BaseModel):
    biacromial: int
    bitrocanter: int
    biliaco: int
    torax: int
    humero: int
    carpo: int
    femur: int
    tobillo: int
    fecha : date 
    id_paciente: int
    
class MedidasHuesosCreate(MedidasHuesosBase):
    pass

class MedidasHuesosUpdate(MedidasHuesosBase):
    pass

class MedidasHuesos(MedidasHuesosBase):
    id_huesos: int | None=None
    
    class Config:
        from_attributes = True
    
    
### Fhir_Patient

class FhirPatientBase(BaseModel):
    id_paciente: int | None=None
    
class FhirPatientCreate(FhirPatientBase):
    pass

class FhirPatientUpdate(PacienteBase):
    pass

class FhirPatient(FhirPatientBase):
    id: int | None=None
    
    class Config:
        from_attributes = True
        
### Fhir_Expedient

class FhirExpedienteBase(BaseModel):
    id_paciente: int | None=None
    #id_patient: int | None=None
    
class FhirExpedienteCreate(FhirExpedienteBase):
    pass

class FhirExpediente(FhirExpedienteBase):
    id_patient: int | None=None