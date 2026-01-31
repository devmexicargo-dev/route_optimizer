import os
from datetime import datetime

import pandas as pd


FILE_PATH = "historial_rutas.xlsx"


def guardar_rutas_excel(rutas, usuario):
    """
    Guarda el historial de rutas en un archivo Excel.
    Este método está BLINDADO: si falla Excel o openpyxl,
    NO rompe la aplicación.
    """

    try:
        rows = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for ruta in rutas:
            vehiculo = ruta.get("vehiculo")

            for orden, parada in enumerate(ruta.get("paradas", [])):

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
                    "direccion": parada.get("direccion"),
                    "llegada": parada.get("llegada"),
                    "espera_min": parada.get("espera"),
                    "salida": parada.get("salida"),
                })

        if not rows:
            print("ℹ️ No hay datos para guardar en el historial.")
            return

        df_nuevo = pd.DataFrame(rows)

        # Si el archivo existe, intentamos concatenar
        if os.path.exists(FILE_PATH):
            try:
                df_existente = pd.read_excel(FILE_PATH)
                df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
            except Exception as e:
                print("⚠️ No se pudo leer el Excel existente, se recreará.")
                print("Detalle:", e)
                df_final = df_nuevo
        else:
            df_final = df_nuevo

        # Intentar guardar
        df_final.to_excel(FILE_PATH, index=False)
        print("✅ Historial de rutas guardado correctamente.")

    except ImportError as e:
        # Caso típico: openpyxl no instalado
        print("⚠️ Excel no guardado (dependencia faltante).")
        print("Detalle:", e)
        print("👉 Ejecuta: pip install openpyxl")

    except Exception as e:
        # Cualquier otro error NO rompe la app
        print("⚠️ Error inesperado al guardar el Excel.")
        print("Detalle:", e)

