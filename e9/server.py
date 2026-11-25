from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Phase Change Diagram Service")

# Puntos de referencia del diagrama (P en MPa, v en m^3/kg)
P_BASE = 0.05
P_CRITICAL = 10.0

V_LIQUID_BASE = 0.00105
V_VAPOR_BASE = 30.00
V_CRITICAL = 0.0035

# Pendientes de interpolación lineal: (v_c - v_0) / (P_c - P_0)
SLOPE_LIQUID = (V_CRITICAL - V_LIQUID_BASE) / (P_CRITICAL - P_BASE)
SLOPE_VAPOR = (V_CRITICAL - V_VAPOR_BASE) / (P_CRITICAL - P_BASE)


class PhaseChangeResponse(BaseModel):
    specific_volume_liquid: float
    specific_volume_vapor: float


@app.get("/phase-change-diagram", response_model=PhaseChangeResponse)
def get_phase_change_diagram(pressure: float = Query(..., description="Presión en MPa")):
    # Interpolación lineal directa
    v_liquid = V_LIQUID_BASE + SLOPE_LIQUID * (pressure - P_BASE)
    v_vapor = V_VAPOR_BASE + SLOPE_VAPOR * (pressure - P_BASE)

    return PhaseChangeResponse(
        specific_volume_liquid=v_liquid,
        specific_volume_vapor=v_vapor
    )