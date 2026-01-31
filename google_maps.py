import os
import random
import time

USE_GOOGLE = os.getenv("USE_GOOGLE_MAPS", "false").lower() == "true"

# ======================================================
# 🚦 FUNCIÓN PRINCIPAL (la que usa tu API)
# ======================================================
def get_time_matrix(addresses):
    if not USE_GOOGLE:
        print("🟢 MODO MOCK ACTIVO → Google Maps NO se usa")
        return fake_time_matrix(len(addresses))
    else:
        print("🔴 MODO GOOGLE ACTIVO → Se usa Google Maps")
        return real_google_time_matrix(addresses)


# ======================================================
# 🟢 MATRIZ FALSA (COSTO $0)
# ======================================================
def fake_time_matrix(n):
    matrix = []

    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0)
            else:
                # tiempos realistas: 5 a 45 min
                row.append(random.randint(300, 2700))
        matrix.append(row)

    return matrix


# ======================================================
# 🔴 MATRIZ REAL (Google) → solo producción
# ======================================================
def real_google_time_matrix(addresses):
    """
    ⚠️ ESTA FUNCIÓN SOLO SE EJECUTA
    CUANDO USE_GOOGLE_MAPS=true
    """
    # AQUÍ VA TU IMPLEMENTACIÓN REAL EXISTENTE
    raise NotImplementedError(
        "Google Maps deshabilitado en modo desarrollo"
    )
