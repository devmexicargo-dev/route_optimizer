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


# =========================
# ⏱️ UTILIDADES DE TIEMPO
# =========================

def segundos_a_hora(segundos, inicio_jornada=6):
    base = timedelta(hours=inicio_jornada)
    return str(base + timedelta(seconds=segundos))[:-3]


def franja_a_segundos(valor: str):
    if valor == "am":
        return (6 * 60 * 60, 14 * 60 * 60)
    if valor == "pm":
        return (14 * 60 * 60, 23 * 60 * 60)
    return (6 * 60 * 60, 23 * 60 * 60)


# =========================
# 🚀 APP
# =========================

app = FastAPI()
app.state.GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def form(request: Request, user: str = Depends(get_current_user)):
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

    # 📍 Direcciones (hasta 19)
    direccion1: str = Form(""), direccion2: str = Form(""),
    direccion3: str = Form(""), direccion4: str = Form(""),
    direccion5: str = Form(""), direccion6: str = Form(""),
    direccion7: str = Form(""), direccion8: str = Form(""),
    direccion9: str = Form(""), direccion10: str = Form(""),
    direccion11: str = Form(""), direccion12: str = Form(""),
    direccion13: str = Form(""), direccion14: str = Form(""),
    direccion15: str = Form(""), direccion16: str = Form(""),
    direccion17: str = Form(""), direccion18: str = Form(""),
    direccion19: str = Form(""),

    # 🕒 Franjas
    franja1: str = Form("all"), franja2: str = Form("all"),
    franja3: str = Form("all"), franja4: str = Form("all"),
    franja5: str = Form("all"), franja6: str = Form("all"),
    franja7: str = Form("all"), franja8: str = Form("all"),
    franja9: str = Form("all"), franja10: str = Form("all"),
    franja11: str = Form("all"), franja12: str = Form("all"),
    franja13: str = Form("all"), franja14: str = Form("all"),
    franja15: str = Form("all"), franja16: str = Form("all"),
    franja17: str = Form("all"), franja18: str = Form("all"),
    franja19: str = Form("all"),

    # ⏳ Esperas
    espera1: int = Form(5), espera2: int = Form(5),
    espera3: int = Form(5), espera4: int = Form(5),
    espera5: int = Form(5), espera6: int = Form(5),
    espera7: int = Form(5), espera8: int = Form(5),
    espera9: int = Form(5), espera10: int = Form(5),
    espera11: int = Form(5), espera12: int = Form(5),
    espera13: int = Form(5), espera14: int = Form(5),
    espera15: int = Form(5), espera16: int = Form(5),
    espera17: int = Form(5), espera18: int = Form(5),
    espera19: int = Form(5),
):
    print("Ruta creada por:", user)

    vehiculos = int(vehiculos)

    # =========================
    # 📍 DIRECCIONES
    # =========================

    direcciones = [
        direccion1, direccion2, direccion3, direccion4, direccion5,
        direccion6, direccion7, direccion8, direccion9, direccion10,
        direccion11, direccion12, direccion13, direccion14, direccion15,
        direccion16, direccion17, direccion18, direccion19
    ]
    direcciones = [d for d in direcciones if d.strip()]

    addresses = [acopio] + direcciones

    # =========================
    # 🕒 VENTANAS HORARIAS
    # =========================

    franjas = [
        franja1, franja2, franja3, franja4, franja5,
        franja6, franja7, franja8, franja9, franja10,
        franja11, franja12, franja13, franja14, franja15,
        franja16, franja17, franja18, franja19
    ]

    time_windows = [(0, 23 * 60 * 60)]  # acopio

    for f in franjas[:len(direcciones)]:
        time_windows.append(franja_a_segundos(f))

    # =========================
    # ⏳ ESPERAS
    # =========================

    esperas = [
        espera1, espera2, espera3, espera4, espera5,
        espera6, espera7, espera8, espera9, espera10,
        espera11, espera12, espera13, espera14, espera15,
        espera16, espera17, espera18, espera19
    ][:len(direcciones)]

    service_times = [0] + [e * 60 for e in esperas]

    # =========================
    # ⚙️ OPTIMIZACIÓN
    # =========================

    time_matrix = get_time_matrix(addresses)

    resultado = optimize_routes(
        time_matrix,
        time_windows,
        service_times,
        vehiculos
    )

    if resultado is None:
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "error": "No fue posible generar una ruta válida."}
        )

    rutas_idx = resultado["routes"]
    no_visitadas_idx = resultado["unserved"]

    # =========================
    # 🗺️ RUTAS VISITADAS
    # =========================

    rutas = []
    MAX_PARADAS_POR_MAPA = 9
    vehiculo_visible = 1

    for ruta in rutas_idx:
        if len(ruta) <= 2:
            continue

        paradas = []
        for paso in ruta:
            idx = paso["node"]
            paradas.append({
                "direccion": addresses[idx],
                "llegada": segundos_a_hora(paso["arrival"]),
                "espera": paso["service"] // 60,
                "salida": segundos_a_hora(paso["arrival"] + paso["service"])
            })

        mapas = []
        inicio = 0

        while inicio < len(paradas) - 1:
            fin = min(inicio + MAX_PARADAS_POR_MAPA, len(paradas))
            tramo = paradas[inicio:fin]

            encoded = [urllib.parse.quote(p["direccion"]) for p in tramo]

            mapas.append({
                "tramo": len(mapas) + 1,
                "desde": tramo[0]["direccion"],
                "hasta": tramo[-1]["direccion"],
                "url": "https://www.google.com/maps/dir/" + "/".join(encoded)
            })

            inicio = fin - 1  # continuidad real

        rutas.append({
            "vehiculo": vehiculo_visible,
            "paradas": paradas,
            "mapas": mapas
        })

        vehiculo_visible += 1

    # =========================
    # ❌ PARADAS NO VISITADAS
    # =========================

    no_visitadas = []

    for idx in no_visitadas_idx:
        no_visitadas.append({
            "direccion": addresses[idx],
            "franja": franjas[idx - 1],
            "espera": esperas[idx - 1]
        })

    guardar_rutas_excel(rutas, user)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "acopio": acopio,
            "rutas": rutas,
            "no_visitadas": no_visitadas
        }
    )


@app.get("/download/excel")
def download_excel(user: str = Depends(get_current_user)):
    file_path = "historial_rutas.xlsx"
    if not os.path.exists(file_path):
        return {"error": "No hay historial disponible"}
    return FileResponse(
        path=file_path,
        filename="historial_rutas.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
