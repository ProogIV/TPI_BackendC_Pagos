# TPI — Microservicio de Pagos

Simula una pasarela bancaria: recibe el cobro de un pedido y responde si fue aprobado o rechazado.
**Python + FastAPI** · Sin base de datos · Puerto **8001**

Forma parte del TPI de Programación IV (Equipo 12). La especificación completa del sistema
(`spec.md`) está en el repositorio orquestador
[TPI_Ecommerce](https://github.com/ProogIV/TPI_Ecommerce).

## Puesta en marcha

```bash
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1          # Windows (PowerShell)
# source venv/bin/activate           # Linux / Mac
pip install -r requirements.txt
cp .env.example .env                 # Windows: Copy-Item .env.example .env
uvicorn app.main:app --port 8001 --reload
```

- Salud: `GET http://127.0.0.1:8001/api/health`
- Documentación automática (OpenAPI): http://127.0.0.1:8001/docs

## Endpoint

`POST /api/payments/process`

```json
{ "order_id": 15, "monto": 370000.00 }
```

| Condición | Respuesta |
|---|---|
| `order_id` o `monto` inválidos (no positivos, faltantes) | `400` `{"error": true, "mensaje": "...", "detalles": [...]}` |
| `monto` hasta el límite (`LIMITE_APROBACION`, por defecto 10.000.000) | `200` `{"estado": "APROBADO", "transaccion_id": "<uuid>", "mensaje": "Pago aprobado"}` |
| `monto` mayor al límite | `200` `{"estado": "RECHAZADO", "transaccion_id": null, "mensaje": "El monto supera el límite autorizado"}` |

## Tests

```bash
pytest
```

## Estructura

```
app/
  main.py       → aplicación FastAPI, endpoints y manejo uniforme de errores
  schemas.py    → esquemas Pydantic (validación y documentación)
  services.py   → lógica de aprobación o rechazo
tests/          → tests con pytest y el TestClient de FastAPI
```

## Decisiones fuera del contenido de la cátedra

| Decisión | Motivo |
|---|---|
| Errores de validación con código `400` en lugar del `422` que usa FastAPI por defecto | El spec pide el mismo formato y los mismos códigos en los tres servicios. |
| `httpx` como dependencia de desarrollo | Lo necesita el `TestClient` de FastAPI para ejecutar los tests. |
