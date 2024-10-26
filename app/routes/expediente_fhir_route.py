from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from crud.expediente_crud import get_expediente_by_id_paciente
from crud.paciente_crud import get_paciente_by_id
from schemas.schemas import FhirExpedienteCreate
from fhir.resources.bundle import Bundle
from fhir.resources.observation import Observation
from fhir.resources.allergyintolerance import AllergyIntolerance
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
    
    response = requests.get(f"{FHIR_SERVER_URL}/Patient/{expediente.id_patient}") 
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Patient no encontrado en el servidor")
    
    paciente = get_paciente_by_id(db, id_paciente=expediente.id_paciente)
    nombre_paciente = paciente.nombre
    
    fhir_patient_data = response.json()
    
    def nombre_coincide(nombre_paciente: str, fhir_patient_data: dict) -> bool:
        fhir_name = fhir_patient_data.get("name", [{}])[0]
        given_name = fhir_name.get("given", [])    
        nombre_patient = " ".join(given_name)
    
        return nombre_paciente.lower().strip() == nombre_patient.lower().strip()
    
    if not nombre_coincide(nombre_paciente, fhir_patient_data):
        raise HTTPException(status_code=400, detail="El ID de FHIR no corresponde al paciente en el sistema.")
     
    #Asegurarse de que 'datos' es un string e intentar deserializarlo
    if isinstance(db_pacienteExp.datos, str):
        datos = json.loads(db_pacienteExp.datos)
    else:
        raise ValueError("`datos` no es un string válido")

    # Imprimir la estructura del JSON para ver su contenido
    #print(f"Estructura del JSON `datos`: {datos}")

    antecedentes_medicos = datos.get("antecedentesMedicos", {}) ###METODO PARA PODER VER LOS CAMPOS DE UN OBJETO JSON, DENTRO DE UN JSON
    motivoSalud = antecedentes_medicos.get("motivo")
    saludActual = antecedentes_medicos.get("saludActual")
    
    antecedentes_patologicos = datos.get("antecedentesPatologicos", {})
    enfermedadesInfecciosas = antecedentes_patologicos.get("enfermedadesInfecciosas", []) ###ACCEDER A LAS LISTAS
    texto_enfermedadesInfecciosas = ", ".join(enfermedadesInfecciosas) ### SE CONVIERTE EN TEXTO EL ARREGLO COMPLETO (LISTA)
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
        
    print(f"Motivo: {motivoSalud}")
    print(f"Salud Actual: {saludActual}")
    print(f"Enfermedades Infecciosas:{enfermedadesInfecciosas}")
    print(f"Otros Infecciosos: {otrosInfecciosos}")
    print(f"Enfermedades Crónicas:{enfermedadesCronicas}")
    print(f"Otros Crónicos: {otrosCronicos}")
    print(f"Consumo: {consumoSustancias}")
    print(f"Otras sustancias: {otrosConsumos}")
    print(f"Alergías: {alergias}")
    print(f"Cirugías: {cirugias}")
    print(f"Obstetricos: {opcionesObstetricos}") 
    print(f"Periodos: {periodosMenstruales}") 
    print(f"Anticonceptivos: {usoAnticonceptivos}") 
    print(f"Cuales: {nombreAnticonceptivos}") 
    print(f"Tiempo de uso: {tiempoUso}") 
    print(f"Climaterio: {condicionClimaterio}")
    print(f"Tratamiento: {opcionesTratamiento}")
    print(f"Otros tratamientos: {otrosTratamientos}")
    print(f"Alopatas: {alopatas}")
    print(f"Cambios en el apetito: {cambiosApetito}")
    print(f"Boca seca: {bocaSeca}")
    print(f"Nauseas: {nauseas}")
    print(f"Hiperglucemia: {hiperglucemia}")
    print(f"Sintomas actuales (opciones): {opcionesSintomas}")
    print(f"Dietas: {dietas}")
    print(f"Trastornos: {trastornos}")
    print(f"Actividad fisica: {actividadFisica}")
    print(f"Tipo: {tipoEjercicio}")
    print(f"Frecuencia: {frecuenciaEjercicio}")
    print(f"Comidas al día: {comidasDia}")
    print(f"Quien prepara la comida: {preparacionComidas}")
    print(f"Tipo de apetito: {tipoApetito}")
    print(f"Tratamiento de control de peso: {opcionControlPeso}")
    print(f"Razon del tratamiento: {razonTratamiento}")
    print(f"Resultados esperados del tratamiento: {resultados}")
    print(f"Uso de medicamentos para bajar de peso: {medicamentos}")
    print(f"Nombre de los medicamentos: {nombreMedicamentos}")
    print(f"Cambio de peso: {cambioPeso}")
    print(f"Cirugia para perder peso: {cirugiaPeso}")
    print(f"Consumo de agua: {consumoAgua}") 
    
    try:
        id_patient = expediente.id_patient

        #Recursos
        motivo_consulta = Observation.construct(
            status="final",
            # code={
            #     "coding": [
            #         {
            #             "system": "http://loinc.org",
            #             "code": "29299-5",  # Código LOINC para Motivo de consulta
            #             "display": "Reason for visit",
            #         }
            #     ]
            # },
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=motivoSalud,
        )

        salud_actual = Observation.construct(
            status="final",
            # code={
            #     "coding": [
            #         {
            #             "system": "http://loinc.org",
            #             "code": "11323-3",  # Código LOINC para Estado de salud general
            #             "display": "Health status",
            #         }
            #     ]
            # },
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=saludActual
        )

        enfermedades_infecciosas = Condition.construct(
            #clinicalStatus=CodeableConcept.construct(
            #    coding=[
            #        Coding.construct(
            #            system="http://terminology.hl7.org/CodeSystem/condition-clinical",
            #            code="active",
            #        )
            #    ]
            #),
            #verificationStatus=CodeableConcept.construct(
            #    coding=[
            #        Coding.construct(
            #            system="http://terminology.hl7.org/CodeSystem/condition-verification",
            #            code="confirmed",
            #        )
            #    ]
            #),
            #category=[
            #    CodeableConcept.construct(
            #        coding=[
            #            Coding.construct(
            #                system="http://terminology.hl7.org/CodeSystem/condition-category",
            #                code="encounter-diagnosis",
            #                display="Encounter Diagnosis",
            #            )
            #        ]
            #    )
            #],
            code=CodeableConcept.construct(
                text=texto_enfermedadesInfecciosas,
                #coding=[
                #    Coding.construct(
                #        system="http://loinc.org",
                #        code="29299-5",
                #        display="Reason for visit",
                #    )
                #   ]
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
            #note=[{"text": "Tiene chorro pq tomó agua de los bebederos de la universidad"}],
        )
        
        otros_infecciosos = Condition.construct(
            code=CodeableConcept.construct(
                text=otrosInfecciosos
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        enfermedades_cronicas = Condition.construct(
             code=CodeableConcept.construct(
                text=texto_enfermedadesCronicas
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        otros_cronicos = Condition.construct(
            code=CodeableConcept.construct(
                text=otrosCronicos
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        consumo_sustancias = Condition.construct( ###CAMBIAR A OBSERVATION
            code=CodeableConcept.construct(
                text=texto_consumoSustancias
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        otros_consumos = Condition.construct( ###CAMBIAR A OBSERVATION
            code = CodeableConcept.construct(
                text=otrosConsumos
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        alergias_resource = AllergyIntolerance.construct(
            #clinicalStatus="active",
            #verificationStatus="confirmed",
            #type="allergy", 
            #category=["food"],
            #criticality="low",
            code=CodeableConcept.construct(
                #coding=[
                #    Coding.construct(
                #        system="http://snomed.info/sct",
                #        code="91935009",
                #        display="Allergy to peanuts",
                #    )
                #]
                text=alergias
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
            #reaction=[
            #    {
            #        "manifestation": [
            #            {
            #                "coding": [
            #                    {
            #                        "system": "http://snomed.info/sct",
            #                        "code": "247472004",
            #                        "display": "Hives",
            #                    }
            #                ]
            #            }
            #        ],
            #        "severity": "severe",
            #    }
            #],
        )
        
        cirugias_resource = Procedure.construct(
            status="completed",
            code=CodeableConcept.construct(
            #    coding=[
            #        Coding.construct(
            #            system="http://snomed.info/sct",
            #            code="387713003",
            #            display="Bariatric surgery",
            #        )
            #    ]
            text=cirugias
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            reportedBoolean=True,
        )
        
        gineco_obstetricos = Condition.construct(
            code=CodeableConcept.construct(
                text=texto_opcionesObstetricos
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        periodos_menstruales = Condition.construct(
            code=CodeableConcept.construct(
                text=periodosMenstruales
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        uso_anticonceptivos = Condition.construct(
            code=CodeableConcept.construct(
                text=usoAnticonceptivos
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        nombre_anticonceptivos = Condition.construct(
            code=CodeableConcept.construct(
                text=nombreAnticonceptivos
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        tiempo_uso = Condition.construct(
            code=CodeableConcept.construct(
                text=tiempoUso
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        climaterio = Condition.construct(
            code=CodeableConcept.construct(
                text=condicionClimaterio
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        tratamiento = MedicationStatement.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            dosage=[
                {
                    "text": texto_opcionesTratamiento
                }
            ]
        )
                
        otros_tratamientos = MedicationStatement.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            dosage=[
                {
                    "text": otrosTratamientos
                }
            ]
        )
        
        tratamientos_alopatas = MedicationStatement.construct(
           subject=Reference.construct(reference=f"Patient/{id_patient}"),
            dosage=[
                {
                    "text": alopatas
                }
            ]
        )
         
        # tratamiento = MedicationStatement.construct(
        #     status="active",
        #     medicationCodeableConcept=CodeableConcept.construct(
        #         coding=[
        #             Coding.construct(
        #                 system="http://www.nlm.nih.gov/research/umls/rxnorm",
        #                 code="104376",
        #                 display="PIÑALIM",
        #             )
        #         ]
        #     ),
        #     subject={"reference": f"Patient/{id_patient}"},
        #     dosage=[
        #         {
        #             "text": texto_opcionesTratamiento,
        #             "asNeededBoolean": False,
        #             "route": {
        #                 "coding": [
        #                     {
        #                         "system": "http://snomed.info/sct",
        #                         "code": "26643006",
        #                         "display": "Oral route",
        #                     }
        #                 ]
        #             },
        #             "doseAndRate": [
        #                 {
        #                     "doseQuantity": {
        #                         "value": 1,
        #                         "unit": "tablet",
        #                         "system": "http://unitsofmeasure.org",
        #                         "code": "tablet",
        #                     }
        #                 }
        #             ],
        #         }
        #     ],
        # )
            
        cambios_apetito = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=cambiosApetito,
        )
        
        boca_seca = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=bocaSeca,
        )
        
        efecto_nauseas = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=nauseas,
        )
        
        efecto_hiperglucemia = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=hiperglucemia,
        )
        
        sintomas_actuales = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=texto_opcionesSintomas,
        )
        
        nutricion_dietas = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=dietas,
        )
        
        nutricion_trastornos = Condition.construct(
            code=CodeableConcept.construct(
                text=trastornos
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}")
        )
        
        actividad_fisica = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=actividadFisica,
        )
        
        tipo_ejercicio = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=tipoEjercicio,
        )
        
        frecuencia_ejercicio = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=frecuenciaEjercicio,
        )
        
        comidas_dia = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=comidasDia,
        )
        
        preparacion_comidas = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=preparacionComidas,
        )
        
        tipo_apetito = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=tipoApetito,
        )
        
        control_peso = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=opcionControlPeso,
        )
        
        razon_tratamiento = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=razonTratamiento,
        )
        
        resultados_tratamiento = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=resultados,
        )
        
        medicamentos_peso = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=medicamentos,
        )
        
        nombre_medicamentos = MedicationStatement.construct(
           subject=Reference.construct(reference=f"Patient/{id_patient}"),
            dosage=[
                {
                    "text": nombreMedicamentos
                }
            ]
        )
        
        cambio_peso = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=cambioPeso,
        )
        
        cirugia_peso = Procedure.construct(
            status="completed",
            code=CodeableConcept.construct(
            text=cirugiaPeso
            ),
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            reportedBoolean=True,
        )
        
        consumo_agua = Observation.construct(
            subject=Reference.construct(reference=f"Patient/{id_patient}"),
            valueString=consumoAgua,
        )
        
        # Crear el Bundle FHIR de tipo transaction
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
                    "request": {"method": "POST", "url": "AllergyIntolerance"}
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

        # Convertir el Bundle a JSON
        bundle_json = bundle.json()

        # Enviar el Bundle al servidor HAPI FHIR
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
