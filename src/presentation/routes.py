"""HTTP routes and template rendering for the transport management app."""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.config import settings
from src.presentation.dependencies import get_current_user, require_role
from src.services.auth_service import auth_service
from src.services.camion_service import camion_service
from src.services.chofer_service import chofer_service
from src.services.hora_service import hora_service
from src.services.ruta_service import ruta_service

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()

EDIT_ROLES = ("admin", "dispatcher")


def flash(request: Request, message: str, kind: str = "success") -> None:
    """Store a one-shot flash message in the session."""
    request.session["flash"] = {"message": message, "kind": kind}


def render(request: Request, template: str, status_code: int = 200, **ctx):
    """Render a template, injecting the flash message and the logged-in user."""
    ctx.setdefault("flash", request.session.pop("flash", None))
    ctx.setdefault("user", request.session.get("user"))
    ctx.setdefault("app_name", settings.app_name)
    return templates.TemplateResponse(request, template, ctx, status_code=status_code)


def _chofer_form(chofer: Optional[dict] = None, posted: Optional[dict] = None) -> dict:
    if posted:
        return posted
    if chofer:
        return {
            "nombre": chofer["nombre"],
            "cedula": chofer["cedula"] or "",
            "licencia": chofer["licencia"] or "",
            "telefono": chofer["telefono"] or "",
            "estado": chofer["estado"],
        }
    return {"nombre": "", "cedula": "", "licencia": "", "telefono": "", "estado": "activo"}


def _camion_form(camion: Optional[dict] = None, posted: Optional[dict] = None) -> dict:
    if posted:
        return posted
    if camion:
        return {
            "placa": camion["placa"],
            "marca": camion["marca"] or "",
            "modelo": camion["modelo"] or "",
            "anio": camion["anio"] if camion["anio"] is not None else "",
            "capacidad": camion["capacidad"] if camion["capacidad"] is not None else "",
            "estado": camion["estado"],
        }
    return {"placa": "", "marca": "", "modelo": "", "anio": "", "capacidad": "", "estado": "activo"}


def _ruta_form(ruta: Optional[dict] = None, posted: Optional[dict] = None) -> dict:
    if posted:
        return posted
    if ruta:
        return {
            "origen": ruta["origen"],
            "destino": ruta["destino"],
            "distancia_km": ruta["distancia_km"],
            "duracion_min": ruta["duracion_min"] if ruta["duracion_min"] is not None else "",
            "estado": ruta["estado"],
        }
    return {"origen": "", "destino": "", "distancia_km": "", "duracion_min": "", "estado": "activa"}


# --------------------------------------------------------------------------- auth


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if request.session.get("user"):
        return RedirectResponse("/dashboard", status_code=303)
    return render(request, "auth/login.html")


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = auth_service.verify_credentials(username.strip(), password)
    if user is None:
        return render(request, "auth/login.html", status_code=401, error="Usuario o contraseña incorrectos")
    request.session["user"] = user.model_dump(mode="json", exclude={"password_hash"})
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, _user=Depends(get_current_user)):
    return render(
        request,
        "dashboard.html",
        count_choferes=chofer_service.count_choferes(),
        count_camiones=camion_service.count_camiones(),
        count_rutas=ruta_service.count_rutas(),
        count_horas=hora_service.count_horas(),
    )


# ----------------------------------------------------------------------- choferes


@router.get("/choferes", response_class=HTMLResponse)
def list_choferes(request: Request, q: str = "", _user=Depends(get_current_user)):
    return render(request, "choferes/list.html", choferes=chofer_service.list_choferes(q), q=q)


@router.get("/choferes/new", response_class=HTMLResponse)
def new_chofer(request: Request, _user=Depends(require_role(*EDIT_ROLES))):
    return render(request, "choferes/form.html", chofer=None, form=_chofer_form())


@router.post("/choferes/new", response_class=HTMLResponse)
def create_chofer(
    request: Request,
    name: str = Form(""),
    cedula: str = Form(""),
    licencia: str = Form(""),
    telefono: str = Form(""),
    _user=Depends(require_role(*EDIT_ROLES)),
):
    try:
        chofer_service.create_chofer(name, cedula, licencia, telefono)
    except ValueError as exc:
        posted = {"nombre": name, "cedula": cedula, "licencia": licencia, "telefono": telefono, "estado": "activo"}
        return render(request, "choferes/form.html", status_code=422, chofer=None, form=_chofer_form(posted=posted), error=str(exc))
    flash(request, "Chofer creado exitosamente.")
    return RedirectResponse("/choferes", status_code=303)


@router.get("/choferes/{chofer_id}/edit", response_class=HTMLResponse)
def edit_chofer(request: Request, chofer_id: int, _user=Depends(require_role(*EDIT_ROLES))):
    chofer = chofer_service.get_chofer(chofer_id)
    if chofer is None:
        flash(request, "Chofer no encontrado.", "error")
        return RedirectResponse("/choferes", status_code=303)
    return render(request, "choferes/form.html", chofer=chofer, form=_chofer_form(chofer))


@router.post("/choferes/{chofer_id}/edit", response_class=HTMLResponse)
def update_chofer(
    request: Request,
    chofer_id: int,
    name: str = Form(""),
    cedula: str = Form(""),
    licencia: str = Form(""),
    telefono: str = Form(""),
    estado: str = Form("activo"),
    _user=Depends(require_role(*EDIT_ROLES)),
):
    chofer = chofer_service.get_chofer(chofer_id)
    if chofer is None:
        flash(request, "Chofer no encontrado.", "error")
        return RedirectResponse("/choferes", status_code=303)
    data = {"nombre": name, "cedula": cedula, "licencia": licencia, "telefono": telefono, "estado": estado}
    try:
        chofer_service.update_chofer(chofer_id, data)
    except ValueError as exc:
        posted = dict(data)
        return render(request, "choferes/form.html", status_code=422, chofer=chofer, form=_chofer_form(posted=posted), error=str(exc))
    flash(request, "Chofer actualizado exitosamente.")
    return RedirectResponse("/choferes", status_code=303)


@router.post("/choferes/{chofer_id}/delete")
def delete_chofer(request: Request, chofer_id: int, _user=Depends(require_role(*EDIT_ROLES))):
    chofer_service.delete_chofer(chofer_id)
    flash(request, "Chofer eliminado exitosamente.")
    return RedirectResponse("/choferes", status_code=303)


# ----------------------------------------------------------------------- camiones


@router.get("/camiones", response_class=HTMLResponse)
def list_camiones(request: Request, q: str = "", _user=Depends(get_current_user)):
    return render(request, "camiones/list.html", camiones=camion_service.list_camiones(q), q=q)


@router.get("/camiones/new", response_class=HTMLResponse)
def new_camion(request: Request, _user=Depends(require_role(*EDIT_ROLES))):
    return render(request, "camiones/form.html", camion=None, form=_camion_form())


@router.post("/camiones/new", response_class=HTMLResponse)
def create_camion(
    request: Request,
    placa: str = Form(""),
    marca: str = Form(""),
    modelo: str = Form(""),
    anio: str = Form(""),
    capacidad: str = Form(""),
    _user=Depends(require_role(*EDIT_ROLES)),
):
    try:
        camion_service.create_camion(placa, marca, modelo, anio, capacidad)
    except ValueError as exc:
        posted = {"placa": placa, "marca": marca, "modelo": modelo, "anio": anio, "capacidad": capacidad, "estado": "activo"}
        return render(request, "camiones/form.html", status_code=422, camion=None, form=_camion_form(posted=posted), error=str(exc))
    flash(request, "Camión creado exitosamente.")
    return RedirectResponse("/camiones", status_code=303)


@router.get("/camiones/{camion_id}/edit", response_class=HTMLResponse)
def edit_camion(request: Request, camion_id: int, _user=Depends(require_role(*EDIT_ROLES))):
    camion = camion_service.get_camion(camion_id)
    if camion is None:
        flash(request, "Camión no encontrado.", "error")
        return RedirectResponse("/camiones", status_code=303)
    return render(request, "camiones/form.html", camion=camion, form=_camion_form(camion))


@router.post("/camiones/{camion_id}/edit", response_class=HTMLResponse)
def update_camion(
    request: Request,
    camion_id: int,
    placa: str = Form(""),
    marca: str = Form(""),
    modelo: str = Form(""),
    anio: str = Form(""),
    capacidad: str = Form(""),
    estado: str = Form("activo"),
    _user=Depends(require_role(*EDIT_ROLES)),
):
    camion = camion_service.get_camion(camion_id)
    if camion is None:
        flash(request, "Camión no encontrado.", "error")
        return RedirectResponse("/camiones", status_code=303)
    data = {"placa": placa, "marca": marca, "modelo": modelo, "anio": anio, "capacidad": capacidad, "estado": estado}
    try:
        camion_service.update_camion(camion_id, data)
    except ValueError as exc:
        posted = dict(data)
        return render(request, "camiones/form.html", status_code=422, camion=camion, form=_camion_form(posted=posted), error=str(exc))
    flash(request, "Camión actualizado exitosamente.")
    return RedirectResponse("/camiones", status_code=303)


@router.post("/camiones/{camion_id}/delete")
def delete_camion(request: Request, camion_id: int, _user=Depends(require_role(*EDIT_ROLES))):
    camion_service.delete_camion(camion_id)
    flash(request, "Camión eliminado exitosamente.")
    return RedirectResponse("/camiones", status_code=303)


# -------------------------------------------------------------------------- rutas


@router.get("/rutas", response_class=HTMLResponse)
def list_rutas(request: Request, q: str = "", _user=Depends(get_current_user)):
    return render(request, "rutas/list.html", rutas=ruta_service.list_rutas(q), q=q)


@router.get("/rutas/new", response_class=HTMLResponse)
def new_ruta(request: Request, _user=Depends(require_role(*EDIT_ROLES))):
    return render(request, "rutas/form.html", ruta=None, form=_ruta_form())


@router.post("/rutas/new", response_class=HTMLResponse)
def create_ruta(
    request: Request,
    origen: str = Form(""),
    destino: str = Form(""),
    distancia_km: str = Form(""),
    duracion_min: str = Form(""),
    _user=Depends(require_role(*EDIT_ROLES)),
):
    try:
        ruta_service.create_ruta(origen, destino, distancia_km, duracion_min)
    except ValueError as exc:
        posted = {"origen": origen, "destino": destino, "distancia_km": distancia_km, "duracion_min": duracion_min, "estado": "activa"}
        return render(request, "rutas/form.html", status_code=422, ruta=None, form=_ruta_form(posted=posted), error=str(exc))
    flash(request, "Ruta creada exitosamente.")
    return RedirectResponse("/rutas", status_code=303)


@router.get("/rutas/{ruta_id}/edit", response_class=HTMLResponse)
def edit_ruta(request: Request, ruta_id: int, _user=Depends(require_role(*EDIT_ROLES))):
    ruta = ruta_service.get_ruta(ruta_id)
    if ruta is None:
        flash(request, "Ruta no encontrada.", "error")
        return RedirectResponse("/rutas", status_code=303)
    return render(request, "rutas/form.html", ruta=ruta, form=_ruta_form(ruta))


@router.post("/rutas/{ruta_id}/edit", response_class=HTMLResponse)
def update_ruta(
    request: Request,
    ruta_id: int,
    origen: str = Form(""),
    destino: str = Form(""),
    distancia_km: str = Form(""),
    duracion_min: str = Form(""),
    estado: str = Form("activa"),
    _user=Depends(require_role(*EDIT_ROLES)),
):
    ruta = ruta_service.get_ruta(ruta_id)
    if ruta is None:
        flash(request, "Ruta no encontrada.", "error")
        return RedirectResponse("/rutas", status_code=303)
    data = {"origen": origen, "destino": destino, "distancia_km": distancia_km, "duracion_min": duracion_min, "estado": estado}
    try:
        ruta_service.update_ruta(ruta_id, data)
    except ValueError as exc:
        posted = dict(data)
        return render(request, "rutas/form.html", status_code=422, ruta=ruta, form=_ruta_form(posted=posted), error=str(exc))
    flash(request, "Ruta actualizada exitosamente.")
    return RedirectResponse("/rutas", status_code=303)


@router.post("/rutas/{ruta_id}/delete")
def delete_ruta(request: Request, ruta_id: int, _user=Depends(require_role(*EDIT_ROLES))):
    ruta_service.delete_ruta(ruta_id)
    flash(request, "Ruta eliminada exitosamente.")
    return RedirectResponse("/rutas", status_code=303)


# -------------------------------------------------------------------------- horas


@router.get("/horas", response_class=HTMLResponse)
def list_horas(request: Request, _user=Depends(get_current_user)):
    return render(request, "horas/list.html", horas=hora_service.list_horas())


@router.get("/horas/new", response_class=HTMLResponse)
def new_hora(request: Request, _user=Depends(require_role(*EDIT_ROLES))):
    return render(
        request,
        "horas/form.html",
        hora=None,
        form={"chofer_id": "", "ruta_id": "", "fecha": "", "horas": ""},
        choferes=hora_service.get_choferes_choices(),
        rutas=hora_service.get_rutas_choices(),
    )


@router.post("/horas/new", response_class=HTMLResponse)
def create_hora(
    request: Request,
    chofer_id: str = Form(""),
    ruta_id: str = Form(""),
    fecha: str = Form(""),
    horas: str = Form(""),
    _user=Depends(require_role(*EDIT_ROLES)),
):
    try:
        hora_service.create_hora(chofer_id, ruta_id, fecha, horas)
    except ValueError as exc:
        posted = {"chofer_id": chofer_id, "ruta_id": ruta_id, "fecha": fecha, "horas": horas}
        return render(
            request,
            "horas/form.html",
            status_code=422,
            hora=None,
            form=posted,
            choferes=hora_service.get_choferes_choices(),
            rutas=hora_service.get_rutas_choices(),
            error=str(exc),
        )
    flash(request, "Horas registradas exitosamente.")
    return RedirectResponse("/horas", status_code=303)


@router.post("/horas/{hora_id}/delete")
def delete_hora(request: Request, hora_id: int, _user=Depends(require_role(*EDIT_ROLES))):
    hora_service.delete_hora(hora_id)
    flash(request, "Registro de horas eliminado exitosamente.")
    return RedirectResponse("/horas", status_code=303)
