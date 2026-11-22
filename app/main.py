"""
Servicio de Pagos (TPI Programación IV): simula una pasarela bancaria. No tiene base de datos.

Se ejecuta con:  uvicorn app.main:app --port 8001 --reload
Documentación automática (OpenAPI):  http://127.0.0.1:8001/docs
"""

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import services
from .schemas import ErrorResponse, PagoRequest, PagoResponse

load_dotenv()

app = FastAPI(
    title="TPI — Servicio de Pagos",
    description="Simula una pasarela bancaria: aprueba o rechaza el cobro de un pedido.",
    version="1.0.0",
)


# --- Formato uniforme de errores: {"error": true, "mensaje": ...} (spec.md, sección 3) ---

@app.exception_handler(RequestValidationError)
async def error_de_validacion(request: Request, exc: RequestValidationError):
    # FastAPI responde 422 por defecto; el spec pide 400 con el mismo formato que los otros servicios
    detalles = [
        {"campo": ".".join(str(parte) for parte in error["loc"][1:]), "mensaje": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content={"error": True, "mensaje": "Error de validación en los datos enviados", "detalles": detalles},
    )


@app.exception_handler(StarletteHTTPException)
async def error_http(request: Request, exc: StarletteHTTPException):
    # Cubre, por ejemplo, el 404 de una ruta inexistente
    return JSONResponse(status_code=exc.status_code, content={"error": True, "mensaje": str(exc.detail)})


# --- Endpoints ---

@app.get("/api/health", tags=["Salud"])
def health_check():
    return {"status": "ok", "service": "pagos"}


@app.post(
    "/api/payments/process",
    response_model=PagoResponse,
    tags=["Pagos"],
    responses={400: {"model": ErrorResponse, "description": "Datos inválidos"}},
)
def procesar_pago(pago: PagoRequest):
    """Aprueba el cobro si el monto no supera el límite; si lo supera, lo rechaza."""
    return services.procesar_pago(pago.order_id, pago.monto)


# --- Documentación OpenAPI acorde a lo que realmente responde la API ---

def openapi_personalizado():
    """
    FastAPI agrega solo una respuesta 422 a la documentación de cada endpoint con datos de entrada.
    Como nuestro manejador de errores responde 400 (con el formato del spec), quitamos el 422
    para que /docs muestre lo que la API hace de verdad.
    """
    if app.openapi_schema:
        return app.openapi_schema

    esquema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    for ruta in esquema["paths"].values():
        for operacion in ruta.values():
            operacion.get("responses", {}).pop("422", None)

    app.openapi_schema = esquema
    return esquema


app.openapi = openapi_personalizado
