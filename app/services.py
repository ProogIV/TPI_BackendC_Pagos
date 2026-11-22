"""Lógica de la pasarela simulada (spec.md, sección 4.3)."""

import os
import uuid

from .schemas import PagoResponse

LIMITE_POR_DEFECTO = 10_000_000


def obtener_limite() -> float:
    """Monto máximo que se aprueba. Se lee del .env para poder cambiarlo sin tocar el código."""
    return float(os.getenv("LIMITE_APROBACION", LIMITE_POR_DEFECTO))


def procesar_pago(order_id: int, monto: float) -> PagoResponse:
    # La validación de tipos y de "mayor a cero" ya la hizo Pydantic en el esquema
    if monto <= obtener_limite():
        return PagoResponse(
            estado="APROBADO",
            transaccion_id=str(uuid.uuid4()),  # identificador único, como el comprobante de un banco
            mensaje="Pago aprobado",
        )

    # Caso agregado para poder demostrar el pedido FALLIDO (spec.md, sección 4.3)
    return PagoResponse(
        estado="RECHAZADO",
        transaccion_id=None,
        mensaje="El monto supera el límite autorizado",
    )
