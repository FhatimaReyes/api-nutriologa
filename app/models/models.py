from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from config.database import Base

class Paciente(Base):
    __tablename__ = "pacientes"
    
    id_paciente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    telefono = Column(String)
    genero = Column(String)
    fecha_nacimiento = Column(Date)
    ocupacion = Column(String)
    
    expedientes = relationship("Expediente", back_populates="pacientes",  cascade="all, delete-orphan")
    consultas = relationship("Consulta", back_populates="pacientes", cascade="all, delete-orphan")
    medidas_musculos = relationship("MedidasMusculos", back_populates="pacientes", cascade="all, delete-orphan")
    medidas_huesos = relationship("MedidasHuesos", back_populates="pacientes", cascade="all, delete-orphan")
    
    
    
class Expediente(Base):
    __tablename__ = "expedientes"
    
    id_expediente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_modificacion = Column(Date)
    datos = Column(String) # Este en la bd es tipo json y se debe estructurar en el front
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"))
    
    pacientes = relationship("Paciente", back_populates="expedientes")
    
    
paciente_musculos = Table(
    'paciente_musculos',
    Base.metadata,
    Column('id_paciente', Integer, ForeignKey('pacientes.id_paciente')),
    Column('id_musculos', Integer, ForeignKey('medidas_musculos.id_musculos'))
)  
    
    
class MedidasMusculos(Base):
    __tablename__ = "medidas_musculos"
    
    id_musculos = Column(Integer, primary_key=True, index=True, autoincrement=True)
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
    id_paciente  = Column(Integer, ForeignKey('pacientes.id_paciente'))
    
    pacientes = relationship("Paciente", back_populates="medidas_musculos")
    
    
    
class MedidasHuesos(Base):
    __tablename__ = "medidas_huesos" 
    
    id_huesos = Column(Integer, primary_key=True, index=True, autoincrement=True)
    biacromial = Column(Integer)
    bitrocanter = Column(Integer)
    biliaco = Column(Integer)
    torax = Column(Integer)
    humero = Column(Integer)
    carpo = Column(Integer)
    femur = Column(Integer)
    tobillo = Column(Integer)
    id_paciente = Column(Integer, ForeignKey('pacientes.id_paciente'))
    
    pacientes = relationship("Paciente", back_populates="medidas_huesos")
    
    
paciente_consulta = Table(
    'paciente_consulta',
    Base.metadata,
    Column('id_paciente', Integer, ForeignKey('pacientes.id_paciente')),
    Column('id_consulta', Integer, ForeignKey('consulta.id_consulta'))
)   

    
class Consulta(Base):
    __tablename__ = "consulta"
    
    id_consulta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date)
    pesoafuera = Column(Float)
    tallaafuera = Column(Float)
    tallasentado = Column(Float)
    pesoadentro = Column(Float)
    tallaadentro = Column(Float)
    frecuencia_cardiaca = Column(Integer)
    nivel_oxigeno = Column(Integer)
    temperatura = Column(Float)
    id_paciente = Column(Integer, ForeignKey('pacientes.id_paciente'))
    
    pacientes = relationship("Paciente", back_populates="consultas")
    