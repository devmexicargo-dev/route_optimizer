import os
from auth import get_current_user
from fastapi import Depends
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
def form(
    request: Request,
    user: str = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "user": user
        }
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
    direccion10: str = Form("")
):
    print("Ruta creada por:", user)

    direcciones = [
        d for d in [
            direccion1, direccion2, direccion3, direccion4, direccion5,
            direccion6, direccion7, direccion8, direccion9, direccion10
        ] if d.strip()
    ]
    if len(direcciones) > 10:
        return {"error": "Máximo 10 direcciones permitidas"}
    
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

        # Solo mostrar vehículos que realmente visitan clientes
        # (acopio + al menos 1 parada + regreso)
        if len(paradas) > 2:
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

