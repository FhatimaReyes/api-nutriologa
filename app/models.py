from sqlalchemy import Column, Integer, String, Date, Float
from database import Base

class Paciente(Base):
    __tablename__ = "pacientes"
    
    id_paciente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    telefono = Column(String)
    genero = Column(String)
    fecha_nacimiento = Column(Date)
    ocupacion = Column(String)
    
    
class Expedientes(Base):
    __tablename__ = "expedientes"
    
    id_expediente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_paciente = Column(Integer)
    fecha_modificacion = Column(Date)
    data = Column(String) # Este en la bd es tipo json y se debe estructurar en el front

class Medidas_Musculos(Base):
    __tablename__ = "medidas_musculos"
    
    id_musculos = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_paciente  = Column(Integer)
    bicep = Column(Float)
    tricep = Column(Float)
    subescapular = Column(Float)
    supriliaco = Column(Float)
    bicep_relajado = Column(Float)
    bicep_contraido = Column(Float)
    antebrazo = Column(Float)
    abdomen = Column(Float)
    muslo = Column(Float)
    gemelo = Column(Float)
    torax = Column(Float)
    gluteo = Column(Float)
    
    
    
class Medidas_Huesos(Base):
    __tablename__ = "medidas_huesos" 
    
    id_huesos = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_paciente = Column(Integer)
    biacromial = Column(Integer)
    bitrocanter = Column(Integer)
    biliaco = Column(Integer)
    torax = Column(Integer)
    humero = Column(Integer)
    carpo = Column(Integer)
    femur = Column(Integer)
    tobillo = Column(Integer)
    
    
class Consulta(Base):
    __tablename__ = "consulta"
    
    id_consulta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_paciente = Column(Integer)
    fecha = Column(Date)
    peso_afuera = Column(Float)
    talla_afuera = Column(Float)
    talla_sentado = Column(Float)
    peso_adentro = Column(Float)
    talla_adentro = Column(Float)
    frecuencia_cardiaca = Column(Integer)
    nivel_oxigeno = Column(Integer)
    temperatura = Column(Float)
    