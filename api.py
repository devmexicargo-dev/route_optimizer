import os
from fastapi.responses import FileResponse
from storage import guardar_rutas_excel
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from google_maps import get_time_matrix
from optimizer import optimize_routes

app = FastAPI()
app.state.GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    return templates.TemplateResponse(
        "form.html",
        {"request": request}
    )


@app.post("/optimize", response_class=HTMLResponse)
def optimize(
    request: Request,
    acopio: str = Form(...),
    vehiculos: int = Form(1),
    direccion1: str = Form(""),
    direccion2: str = Form(""),
    direccion3: str = Form(""),
    direccion4: str = Form(""),
    direccion5: str = Form("")
):
    direcciones = [
        d for d in [
            direccion1, direccion2, direccion3, direccion4, direccion5
        ] if d.strip()
    ]

    addresses = [acopio] + direcciones

    time_matrix = get_time_matrix(addresses)
    print(">>> Vehículos recibidos:", vehiculos)
    rutas_idx = optimize_routes(time_matrix, num_vehicles=vehiculos)

    # 🔹 Convertir índices a direcciones
    import urllib.parse

    rutas = []

    for i in range(vehiculos):
        ruta = rutas_idx[i] if i < len(rutas_idx) else []

        # Convertir índices a direcciones
        paradas = [addresses[idx] for idx in ruta]

        # Construir link Google Maps
        encoded_stops = [urllib.parse.quote(p) for p in paradas]
        maps_url = "https://www.google.com/maps/dir/" + "/".join(encoded_stops)

        rutas.append({
            "vehiculo": i + 1,
            "paradas": paradas,
            "maps_url": maps_url
        })



    guardar_rutas_excel(rutas)
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "acopio": acopio,
            "rutas": rutas
        }
    )

@app.get("/download/excel")
def download_excel():
    file_path = "historial_rutas.xlsx"

    if not os.path.exists(file_path):
        return {"error": "No hay historial disponible todavía"}

    return FileResponse(
        path=file_path,
        filename="historial_rutas.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
