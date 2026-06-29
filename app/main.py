from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, alumnos, tamizajes, cuestionario, resultados, disponibilidad, citas

settings = get_settings()

app = FastAPI(
    title="VitalMind API",
    description="Backend del Ecosistema Integral de Monitoreo y Gestión del Bienestar — FISI UNMSM",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — ajustar origins en producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir al dominio del frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Routers (se irán registrando conforme se implementen) ---
# from app.routers import auth, alumnos, tamizajes, cuestionario, resultados, citas
# app.include_router(auth.router,          prefix="/auth",          tags=["Autenticación"])
# app.include_router(alumnos.router,       prefix="/alumnos",       tags=["Alumnos"])
# app.include_router(tamizajes.router,     prefix="/tamizajes",     tags=["Tamizajes"])
# app.include_router(cuestionario.router,  prefix="/cuestionario",  tags=["Cuestionario Alumno"])
# app.include_router(resultados.router,    prefix="/resultados",    tags=["Resultados"])
# app.include_router(citas.router,         prefix="/citas",         tags=["Agenda y Citas"])

# Registro de routers
app.include_router(auth.router)
app.include_router(alumnos.router)
app.include_router(tamizajes.router)
app.include_router(cuestionario.router)
app.include_router(resultados.router)
app.include_router(disponibilidad.router)
app.include_router(citas.router)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "app": "VitalMind API",
        "version": "0.1.0",
    }