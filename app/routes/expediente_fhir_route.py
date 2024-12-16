from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from crud.expediente_crud import get_expediente_by_id_paciente
from crud.paciente_crud import get_paciente_by_id
from schemas.schemas import FhirExpedienteCreate
from fhir.resources.bundle import Bundle
from fhir.resources.observation import Observation
from fhir.resources.condition import Condition
from fhir.resources.procedure import Procedure
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.reference import Reference
import requests, json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

FHIR_SERVER_URL = "http://localhost:8080/fhir"

@router.post("/expediente_fhir", response_model=dict)
def agregar_expediente_fhir(expediente: FhirExpedienteCreate, db: Session = Depends(get_db)):
    db_pacienteExp = get_expediente_by_id_paciente(db, id_paciente=expediente.id_paciente)
    if db_pacienteExp is None:
        raise HTTPException(status_code=404, detail="El paciente no existe o no cuenta con un expediente, verifique")
    
    
    paciente = get_paciente_by_id(db, id_paciente=expediente.id_paciente)
    nombre_paciente = paciente.nombre
    
    response = requests.get(f"{FHIR_SERVER_URL}/Patient", params={"name": nombre_paciente})
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Patient no encontrado en el servidor")
    
    fhir_data = response.json()
    if not fhir_data.get("entry"):
        raise HTTPException(status_code=404, detail="No se encontraron coincidencias para el paciente en el servidor FHIR")
    
    paciente_fhir = fhir_data["entry"][0]["resource"]
    fhir_id_patient = paciente_fhir["id"]
    
    def nombre_coincide(nombre_paciente: str, fhir_patient_data: dict) -> bool:
        fhir_name = fhir_patient_data.get("name", [{}])[0]
        given_name = fhir_name.get("given", [])    
        nombre_patient = " ".join(given_name)
    
        return nombre_paciente.lower().strip() == nombre_patient.lower().strip()
    
    if not nombre_coincide(nombre_paciente, paciente_fhir):
        raise HTTPException(status_code=400, detail="El ID de FHIR no corresponde al paciente en el sistema.")
     
    if isinstance(db_pacienteExp.datos, str):
        datos = json.loads(db_pacienteExp.datos)
    else:
        raise ValueError("`datos` no es un string válido")

    antecedentes_medicos = datos.get("antecedentesMedicos", {}) 
    motivo = antecedentes_medicos.get("motivo")
    saludActual = antecedentes_medicos.get("saludActual")
    
    antecedentes_patologicos = datos.get("antecedentesPatologicos", {})
    enfermedadesInfecciosas = antecedentes_patologicos.get("enfermedadesInfecciosas", [])
    texto_enfermedadesInfecciosas = ", ".join(enfermedadesInfecciosas)
    otrosInfecciosos = antecedentes_patologicos.get("otrosInfecciosos")
    
    enfermedadesCronicas = antecedentes_patologicos.get("enfermedadesCronicas", [])
    texto_enfermedadesCronicas = ", ".join(enfermedadesCronicas)
    otrosCronicos = antecedentes_patologicos.get("otrosCronicos") 
    
    consumoSustancias = antecedentes_patologicos.get("consumo", [])
    texto_consumoSustancias = ", ".join(consumoSustancias)
    otrosConsumos = antecedentes_patologicos.get("otroConsumo")
    
    alergias = antecedentes_patologicos.get("alergias")
    
    cirugias = antecedentes_patologicos.get("cirugias")
        
    antecedentesObstetricos = datos.get("antecedentesObstetricos", {})
    opcionesObstetricos = antecedentesObstetricos.get("opciones",[])
    texto_opcionesObstetricos = ", ".join(opcionesObstetricos) 
    
    periodosMenstruales = antecedentesObstetricos.get("periodosMenstruales") 
    
    usoAnticonceptivos = antecedentesObstetricos.get("anticonceptivos") 
    
    nombreAnticonceptivos = antecedentesObstetricos.get("cuales") 
    
    tiempoUso = antecedentesObstetricos.get("tiempoUso") 
    
    condicionClimaterio = antecedentesObstetricos.get("climaterio") 
    
    tratamientoTipo = datos.get("tratamiento", {})
    opcionesTratamiento = tratamientoTipo.get("opciones", [])
    texto_opcionesTratamiento = ", ".join(opcionesTratamiento)
    otrosTratamientos = tratamientoTipo.get("otros")
    alopatas = tratamientoTipo.get("alopatas")
    
    farmacosNutricion = datos.get("farmacosNutricion", {})
    cambiosApetito = farmacosNutricion.get("cambiosApetito")
    bocaSeca = farmacosNutricion.get("bocaSeca")
    nauseas = farmacosNutricion.get("nauseas")
    hiperglucemia = farmacosNutricion.get("hiperglucemia")
    
    sintomasActuales = datos.get("sintomasActuales", {})
    opcionesSintomas = sintomasActuales.get("opciones", [])
    texto_opcionesSintomas = ", ".join(opcionesSintomas)
    
    problemasNutricion = datos.get("problemasNutricion", {})
    dietas = problemasNutricion.get("dietas")
    trastornos = problemasNutricion.get("transtornos")
    
    estiloVida = datos.get("estiloVida", {})
    actividadFisica = estiloVida.get("actividadFisica")
    ejercicio = estiloVida.get("ejercicio", {})
    tipoEjercicio = ejercicio.get("tipo")
    frecuenciaEjercicio = ejercicio.get("frecuencia")

    indicadoresDieteticos = estiloVida.get("indicadoresDieteticos", {})
    comidasDia = indicadoresDieteticos.get("comidasDia")
    preparacionComidas = indicadoresDieteticos.get("preparacionComidas")
    
    apetito = estiloVida.get("apetito", {})
    tipoApetito = apetito.get("tipo")

    controlPeso = apetito.get("controlPeso", {})
    opcionControlPeso = controlPeso.get("opcion")
    razonTratamiento = controlPeso.get("razon")
    resultados = controlPeso.get("resultados")
    medicamentos = controlPeso.get("medicamentos")
    nombreMedicamentos = controlPeso.get("cuales")
    cambioPeso = controlPeso.get("cambioPeso")
    cirugiaPeso = controlPeso.get("cirugiaPeso")
    consumoAgua = controlPeso.get("consumoAgua")
        
    # print(f"Motivo: {motivo}")
    # print(f"Salud Actual: {saludActual}")
    # print(f"Enfermedades Infecciosas:{enfermedadesInfecciosas}")
    # print(f"Otros Infecciosos: {otrosInfecciosos}")
    # print(f"Enfermedades Crónicas:{enfermedadesCronicas}")
    # print(f"Otros Crónicos: {otrosCronicos}")
    # print(f"Consumo: {consumoSustancias}")
    # print(f"Otras sustancias: {otrosConsumos}")
    # print(f"Alergías: {alergias}")
    # print(f"Cirugías: {cirugias}")
    # print(f"Obstetricos: {opcionesObstetricos}") 
    # print(f"Periodos: {periodosMenstruales}") 
    # print(f"Anticonceptivos: {usoAnticonceptivos}") 
    # print(f"Cuales: {nombreAnticonceptivos}") 
    # print(f"Tiempo de uso: {tiempoUso}") 
    # print(f"Climaterio: {condicionClimaterio}")
    # print(f"Tratamiento: {opcionesTratamiento}")
    # print(f"Otros tratamientos: {otrosTratamientos}")
    # print(f"Alopatas: {alopatas}")
    # print(f"Cambios en el apetito: {cambiosApetito}")
    # print(f"Boca seca: {bocaSeca}")
    # print(f"Nauseas: {nauseas}")
    # print(f"Hiperglucemia: {hiperglucemia}")
    # print(f"Sintomas actuales (opciones): {opcionesSintomas}")
    # print(f"Dietas: {dietas}")
    # print(f"Trastornos: {trastornos}")
    # print(f"Actividad fisica: {actividadFisica}")
    # print(f"Tipo: {tipoEjercicio}")
    # print(f"Frecuencia: {frecuenciaEjercicio}")
    # print(f"Comidas al día: {comidasDia}")
    # print(f"Quien prepara la comida: {preparacionComidas}")
    # print(f"Tipo de apetito: {tipoApetito}")
    # print(f"Tratamiento de control de peso: {opcionControlPeso}")
    # print(f"Razon del tratamiento: {razonTratamiento}")
    # print(f"Resultados esperados del tratamiento: {resultados}")
    # print(f"Uso de medicamentos para bajar de peso: {medicamentos}")
    # print(f"Nombre de los medicamentos: {nombreMedicamentos}")
    # print(f"Cambio de peso: {cambioPeso}")
    # print(f"Cirugia para perder peso: {cirugiaPeso}")
    # print(f"Consumo de agua: {consumoAgua}") 
    
    try:
        id_patient = fhir_id_patient

        #Recursos
        motivo_consulta = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Motivo de consulta: {motivo}"),
        )

        salud_actual = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Salud actual: {saludActual}")
        )

        enfermedades_infecciosas = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Enfermedades infeccionas: {texto_enfermedadesInfecciosas}"),
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        otros_infecciosos = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Otras enfermedades infecciosas: {otrosInfecciosos}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        enfermedades_cronicas = Condition.construct(
             code=CodeableConcept.construct(
                text=(f"Enfermedades crónicas: {texto_enfermedadesCronicas}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        otros_cronicos = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Otras enfermedades crónicas: {otrosCronicos}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        consumo_sustancias = Condition.construct( ###CAMBIAR A OBSERVATION
            code=CodeableConcept.construct(
                text=(f"Consumo de sustancias: {texto_consumoSustancias}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        otros_consumos = Condition.construct( ###CAMBIAR A OBSERVATION
            code = CodeableConcept.construct(
                text=(f"Otras sustancias: {otrosConsumos}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        alergias_resource = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Alergias: {alergias}"),
        )
        
        cirugias_resource = Procedure.construct(
            status="completed",
            code=CodeableConcept.construct(
            text=(f"Cirugías: {cirugias}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            reportedBoolean=True,
        )
        
        gineco_obstetricos = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Antecedentes gineco-obstétricos: {texto_opcionesObstetricos}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        periodos_menstruales = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Períodos menstruales: {periodosMenstruales}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        uso_anticonceptivos = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Uso de anticonceptivos: {usoAnticonceptivos}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        nombre_anticonceptivos = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"¿Cuáles anticonceptivos?: {nombreAnticonceptivos}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        tiempo_uso = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Tiempo usando anticonceptivos: {tiempoUso}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        climaterio = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Climaterio: {condicionClimaterio}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        tratamiento = MedicationStatement.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            dosage=[
                {
                    "text": (f"Tratamiento: {texto_opcionesTratamiento}")
                }
            ]
        )
                
        otros_tratamientos = MedicationStatement.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            dosage=[
                {
                    "text": (f"Otros tratamientos: {otrosTratamientos}")
                }
            ]
        )
        
        tratamientos_alopatas = MedicationStatement.construct(
           subject=Reference.construct(reference=f"Patient/{id_patient}"),
            dosage=[
                {
                    "text": (f"Medicamentos alópatas: {alopatas}")
                }
            ]
        )
             
        cambios_apetito = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Cambios en el apetito: {cambiosApetito}"),
        )
        
        boca_seca = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Boca seca: {bocaSeca}"),
        )
        
        efecto_nauseas = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Nauseas: {nauseas}"),
        )
        
        efecto_hiperglucemia = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Hiperglucemia: {hiperglucemia}"),
        )
        
        sintomas_actuales = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Síntomas actuales: {texto_opcionesSintomas}"),
        )
        
        nutricion_dietas = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Dietas o tratamientos realizados anteriormente: {dietas}"),
        )
        
        nutricion_trastornos = Condition.construct(
            code=CodeableConcept.construct(
                text=(f"Trastornos de alimentación: {trastornos}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        actividad_fisica = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Actividad fisica: {actividadFisica}"),
        )
        
        tipo_ejercicio = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Tipo de ejercicio: {tipoEjercicio}"),
        )
        
        frecuencia_ejercicio = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Frecuencia de ejercicio: {frecuenciaEjercicio}"),
        )
        
        comidas_dia = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"¿Cuántas comidas hace al día?: {comidasDia}"),
        )
        
        preparacion_comidas = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"¿Quién prepara sus alimentos?: {preparacionComidas}"),
        )
        
        tipo_apetito = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Apetito: {tipoApetito}"),
        )
        
        control_peso = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"¿Ha llevado un tratamiento para control de peso?: {opcionControlPeso}"),
        )
        
        razon_tratamiento = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Razón del tratamiendo de control de peso: {razonTratamiento}"),
        )
        
        resultados_tratamiento = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"¿Obtuvo los resultados esperados del control de peso?: {resultados}"),
        )
        
        medicamentos_peso = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"¿Ha utilizado medicamentos para bajar de peso?: {medicamentos}"),
        )
        
        nombre_medicamentos = MedicationStatement.construct(
           subject=Reference.construct(reference=f"Patient/{id_patient}"),
            dosage=[
                {
                    "text": (f"Nombre de medicamentos para bajar de peso: {nombreMedicamentos}")
                }
            ]
        )
        
        cambio_peso = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"¿Cómo ha fluctuado su peso a lo largo de su vida?: {cambioPeso}"),
        )
        
        cirugia_peso = Procedure.construct(
            status="completed",
            code=CodeableConcept.construct(
            text=(f"¿Se ha sometido a alguna cirugía para perder peso?: {cirugiaPeso}")
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            reportedBoolean=True,
        )
        
        consumo_agua = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=(f"Consumo regular de agua simple al día: {consumoAgua}"),
        )
        
        bundle = Bundle.construct(
            type="transaction",
            entry=[
                {
                    "resource": motivo_consulta,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": salud_actual,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": enfermedades_infecciosas,
                    "request": {"method": "POST", "url": "Condition"}
                 },
                {
                    "resource": otros_infecciosos,
                    "request": {"method": "POST", "url": "Condition"}  
                },
                {
                    "resource": enfermedades_cronicas,
                    "request": {"method": "POST", "url": "Condition"}
                 },
                {
                    "resource": otros_cronicos,
                    "request": {"method": "POST", "url": "Condition"}  
                },
                {
                    "resource": consumo_sustancias,
                    "request": {"method": "POST", "url": "Condition"}  
                },
                {
                    "resource": otros_consumos,
                    "request": {"method": "POST", "url": "Condition"}  
                },
                {
                    "resource": alergias_resource,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": cirugias_resource,
                    "request": {"method": "POST", "url": "Procedure"}
                },
                {
                    "resource": gineco_obstetricos,
                    "request": {"method": "POST", "url": "Condition"}
                },
                {
                    "resource": periodos_menstruales,
                    "request": {"method": "POST", "url": "Condition"}
                },
                {
                    "resource": uso_anticonceptivos,
                    "request": {"method": "POST", "url": "Condition"}
                },
                {
                    "resource": nombre_anticonceptivos,
                    "request": {"method": "POST", "url": "Condition"}
                },
                {
                    "resource": tiempo_uso,
                    "request": {"method": "POST", "url": "Condition"}
                },
                {
                    "resource": climaterio,
                    "request": {"method": "POST", "url": "Condition"}
                },
                {
                    "resource": tratamiento,
                    "request": {"method": "POST", "url": "MedicationStatement"}
                },
                {
                    "resource": otros_tratamientos,
                    "request": {"method": "POST", "url": "MedicationStatement"}
                },
                {
                    "resource": tratamientos_alopatas,
                    "request": {"method": "POST", "url": "MedicationStatement"}
                },
                {
                    "resource": cambios_apetito,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": boca_seca,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": efecto_nauseas,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": efecto_hiperglucemia,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": sintomas_actuales,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": nutricion_dietas,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": nutricion_trastornos,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": actividad_fisica,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": tipo_ejercicio,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": frecuencia_ejercicio,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": comidas_dia,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": preparacion_comidas,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": tipo_apetito,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": control_peso,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": razon_tratamiento,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": resultados_tratamiento,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": medicamentos_peso,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": nombre_medicamentos,
                    "request": {"method": "POST", "url": "MedicationStatement"}
                },
                {
                    "resource": cambio_peso,
                    "request": {"method": "POST", "url": "Observation"}
                },
                {
                    "resource": cirugia_peso,
                    "request": {"method": "POST", "url": "Procedure"}
                },
                {
                    "resource": consumo_agua,
                    "request": {"method": "POST", "url": "Observation"}
                }
            ],
        )

        bundle_json = bundle.json()

        response = requests.post(
            FHIR_SERVER_URL,
            headers={"Content-Type": "application/fhir+json"},
            data=bundle_json,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return {"message": "Recursos agregados exitosamente"}

    except Exception as e:
        raise HTTPException(
            status_code=500,  detail=f"Error al procesar la solicitud: {str(e)}"
        )
