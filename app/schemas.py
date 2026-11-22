"""
Esquemas Pydantic (spec.md, sección 4.3).

FastAPI los usa para validar automáticamente los datos que llegan y para documentar la API
en /docs. Si un dato no cumple el esquema, la petición se rechaza antes de llegar a la lógica.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class PagoRequest(BaseModel):
    order_id: int = Field(gt=0, description="ID del pedido en el servicio de Pedidos", examples=[15])
    monto: float = Field(gt=0, description="Importe a cobrar", examples=[370000.00])


class PagoResponse(BaseModel):
    estado: Literal["APROBADO", "RECHAZADO"]
    transaccion_id: Optional[str] = Field(default=None, description="Comprobante; nulo si se rechaza")
    mensaje: str
