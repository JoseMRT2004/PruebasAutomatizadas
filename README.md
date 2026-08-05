# Gestión de Transporte — Pruebas Automatizadas con Selenium

Proyecto para la **Tarea 4: Pruebas Automatizadas con Selenium** (Programación III, ITLA).

Incluye:

1. **Aplicación base funcional** (FastAPI + SQLite + Jinja2): sistema de gestión de transporte con
   autenticación y operaciones CRUD sobre choferes, camiones, rutas y horas trabajadas.
2. **Suite de pruebas automatizadas** (Selenium + pytest + Page Object Model): más de 15 escenarios
   con camino feliz, prueba negativa y prueba de límites por cada historia de usuario.
3. **Reporte HTML** (`reports/report.html`) y **capturas automáticas** por escenario (`screenshots/`).

## Credenciales de acceso (usuarios iniciales)

| Usuario       | Contraseña     | Rol          | Permisos                          |
| ------------- | -------------- | ------------ | --------------------------------- |
| `admin`       | `admin123`     | administrador| CRUD completo                     |
| `dispatcher`  | `dispatcher123`| despachador  | CRUD completo                     |
| `consultor`   | `consultor123` | consultor    | Solo lectura                      |

## Requisitos

- Python 3.12 y [uv](https://docs.astral.sh/uv/)
- Firefox (para Selenium; el driver `geckodriver` se descarga automáticamente en la primera ejecución)

## Puesta en marcha

```bash
# Instalar dependencias
uv sync

# 1) Levantar la aplicación (http://127.0.0.1:8000)
bash scripts/start_app.sh

# 2) En otra terminal, ejecutar la suite de pruebas (levanta su propia instancia)
bash scripts/run_e2e.sh
```

La suite levanta automáticamente una instancia temporal de la aplicación con una base de datos
SQLite aislada en un puerto libre, la ejecuta contra Firefox y genera el reporte y las capturas.

Opciones útiles:

```bash
HEADLESS=1 uv run pytest -v     # modo sin ventana (servidores/CI)
uv run pytest tests/test_login.py   # solo un flujo
```

## Historias de usuario

Las 5 historias con criterios de aceptación y rechazo están en
[`docs/user-stories.md`](docs/user-stories.md), listas para documentar en Jira o Azure DevOps.
La trazabilidad historia ↔ casos de prueba:

| Historia | Archivo de pruebas | Escenarios |
| --- | --- | --- |
| US-01 Inicio de sesión | `tests/test_login.py` | Feliz, negativa, límites |
| US-02 Gestionar choferes | `tests/test_choferes.py` | Feliz, negativa, límites |
| US-03 Gestionar camiones | `tests/test_camiones.py` | Feliz, negativa, límites |
| US-04 Gestionar rutas | `tests/test_rutas.py` | Feliz, negativa, límites |
| US-05 Registrar horas trabajadas | `tests/test_horas.py` | Feliz, negativa, límites |

## Estructura del proyecto

```
├── src/                    # Aplicación base (FastAPI + SQLite)
│   ├── models/             # Entidades: chofer, camión, ruta, hora de trabajo, usuario
│   ├── services/           # Lógica de negocio y validaciones
│   ├── presentation/
│   │   ├── routes.py       # Endpoints (login + CRUD)
│   │   ├── static/         # CSS monocromático
│   │   └── templates/      # Vistas con menú lateral
├── tests/                  # Suite Selenium (pytest + POM)
│   ├── pages/              # Page Objects (login, choferes, camiones, rutas, horas)
│   └── test_*.py           # Casos por historia de usuario
├── scripts/
│   ├── start_app.sh        # Levanta la aplicación
│   └── run_e2e.sh          # Ejecuta la suite completa
├── reports/report.html     # Reporte HTML de resultados (pytest-html)
├── screenshots/            # Capturas automáticas por escenario
└── docs/
    ├── user-stories.md     # 5 historias de usuario con criterios de aceptación y rechazo
    └── azure-setup.md      # Guía para documentarlas en Jira/Azure DevOps
```

## Entregables de la tarea

| Entregable | Enlace |
| --- | --- |
| Repositorio de código (GitHub) | `https://github.com/JoseMRT2004/<repo>` |
| Tablero Jira / Azure DevOps | (completar) |
| Video demostrativo (YouTube/OneDrive) | (completar) |

> Regla de la tarea: sin acceso público al repositorio, tablero o video la calificación es 0.
> Los enlaces deben ser públicos o con acceso abierto.
