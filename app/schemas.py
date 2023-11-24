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
    id_paciente: int #
    fecha_nacimiento: date | None=None
    ocupacion: str | None=None
    
class ExpedienteCreate(PacienteBase):
    pass

class ExpedienteUpdate(PacienteBase):
    pass

class Expediente(PacienteBase):
    id_Expediente: int | None=None
    
    class Config:
        from_attributes = True