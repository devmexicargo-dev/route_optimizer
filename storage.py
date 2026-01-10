import pandas as pd
from datetime import datetime
import os

FILE_PATH = "historial_rutas.xlsx"


def guardar_rutas_excel(rutas, usuario):
    rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for ruta in rutas:
        vehiculo = ruta["vehiculo"]

        for orden, parada in enumerate(ruta["paradas"]):

            if orden == 0:
                tipo = "ACOPIO SALIDA"
            elif orden == len(ruta["paradas"]) - 1:
                tipo = "ACOPIO REGRESO"
            else:
                tipo = "RECOGIDA"

            rows.append({
                "fecha": timestamp,
                "usuario": usuario,
                "vehiculo": vehiculo,
                "orden": orden,
                "tipo": tipo,
                "direccion": parada["direccion"],
                "llegada": parada["llegada"],
                "espera_min": parada["espera"],
                "salida": parada["salida"]
            })

    if not rows:
        return

    df_nuevo = pd.DataFrame(rows)

    if os.path.exists(FILE_PATH):
        df_existente = pd.read_excel(FILE_PATH)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo

    df_final.to_excel(FILE_PATH, index=False)
