import os
import urllib.parse
from datetime import timedelta

from auth import get_current_user
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from google_maps import get_time_matrix
from optimizer import optimize_routes
from storage import guardar_rutas_excel


# 🕒 Convertir segundos a hora legible
def segundos_a_hora(segundos, inicio_jornada=6):
    base = timedelta(hours=inicio_jornada)
    return str(base + timedelta(seconds=segundos))[:-3]


# 🕒 Convertir franja a segundos
def franja_a_segundos(valor: str):
    if valor == "am":
        return (6 * 60 * 60, 14 * 60 * 60)
    if valor == "pm":
        return (14 * 60 * 60, 23 * 60 * 60)
    return (6 * 60 * 60, 23 * 60 * 60)  # all


app = FastAPI()
app.state.GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def form(
    request: Request,
    user: str = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "form.html",
        {"request": request, "user": user}
    )


@app.post("/optimize", response_class=HTMLResponse)
def optimize(
    request: Request,
    user: str = Depends(get_current_user),

    acopio: str = Form(...),
    vehiculos: int = Form(...),

    direccion1: str = Form(""),
    direccion2: str = Form(""),
    direccion3: str = Form(""),
    direccion4: str = Form(""),
    direccion5: str = Form(""),
    direccion6: str = Form(""),
    direccion7: str = Form(""),
    direccion8: str = Form(""),
    direccion9: str = Form(""),
    direccion10: str = Form(""),

    franja1: str = Form("all"),
    franja2: str = Form("all"),
    franja3: str = Form("all"),
    franja4: str = Form("all"),
    franja5: str = Form("all"),
    franja6: str = Form("all"),
    franja7: str = Form("all"),
    franja8: str = Form("all"),
    franja9: str = Form("all"),
    franja10: str = Form("all"),

    espera1: int = Form(5),
    espera2: int = Form(5),
    espera3: int = Form(5),
    espera4: int = Form(5),
    espera5: int = Form(5),
    espera6: int = Form(5),
    espera7: int = Form(5),
    espera8: int = Form(5),
    espera9: int = Form(5),
    espera10: int = Form(5),
):
    print("Ruta creada por:", user)

    vehiculos = int(vehiculos)

    # 📍 Direcciones
    direcciones = [
        d for d in [
            direccion1, direccion2, direccion3, direccion4, direccion5,
            direccion6, direccion7, direccion8, direccion9, direccion10
        ] if d.strip()
    ]

    addresses = [acopio] + direcciones

    # 🕒 Ventanas horarias
    time_windows = [(0, 23 * 60 * 60)]  # acopio

    franjas = [
        franja1, franja2, franja3, franja4, franja5,
        franja6, franja7, franja8, franja9, franja10
    ]

    for f in franjas[:len(direcciones)]:
        time_windows.append(franja_a_segundos(f))

    # ⏳ Tiempos de espera
    esperas = [
        espera1, espera2, espera3, espera4, espera5,
        espera6, espera7, espera8, espera9, espera10
    ][:len(direcciones)]

    service_times = [0] + [e * 60 for e in esperas]

    # ⏱️ Matriz de tiempos
    time_matrix = get_time_matrix(addresses)

    rutas_idx = optimize_routes(
        time_matrix,
        time_windows,
        service_times,
        vehiculos
    )

    if rutas_idx is None:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "error": "No es posible cumplir las franjas horarias con los vehículos disponibles."
            }
        )

    # 🗺️ Construir resultados + Google Maps link
    rutas = []

    for i, ruta in enumerate(rutas_idx):
        paradas = []

        for paso in ruta:
            idx = paso["node"]
            llegada = segundos_a_hora(paso["arrival"])
            espera_min = paso["service"] // 60
            salida = segundos_a_hora(paso["arrival"] + paso["service"])

            paradas.append({
                "direccion": addresses[idx],
                "llegada": llegada,
                "espera": espera_min,
                "salida": salida
            })

        if len(paradas) > 2:
            encoded = [
                urllib.parse.quote(p["direccion"])
                for p in paradas
            ]
            maps_url = "https://www.google.com/maps/dir/" + "/".join(encoded)

            rutas.append({
                "vehiculo": i + 1,
                "paradas": paradas,
                "maps_url": maps_url
            })

    guardar_rutas_excel(rutas, user)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "acopio": acopio,
            "rutas": rutas
        }
    )


@app.get("/download/excel")
def download_excel(
    user: str = Depends(get_current_user)
):
    file_path = "historial_rutas.xlsx"

    if not os.path.exists(file_path):
        return {"error": "No hay historial disponible todavía"}

    return FileResponse(
        path=file_path,
        filename="historial_rutas.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
