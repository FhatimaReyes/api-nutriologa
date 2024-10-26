from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from config.database  import engine, Base
import routes.paciente_route, routes.expediente_route, routes.consulta_route, routes.medidas_musculos_route, routes.medidas_huesos_route, routes.patient_fhir_route, routes.expediente_fhir_route
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.title = "Nutriologa - API"
app.version = "2.0"

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


# Configurar CORS
origins = [
    "http://localhost:4200",
    # Otros orígenes permitidos, si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
        
app.include_router(routes.paciente_route.router)
app.include_router(routes.expediente_route.router)
app.include_router(routes.consulta_route.router)
app.include_router(routes.medidas_musculos_route.router)
app.include_router(routes.medidas_huesos_route.router)
app.include_router(routes.patient_fhir_route.router)
app.include_router(routes.expediente_fhir_route.router)