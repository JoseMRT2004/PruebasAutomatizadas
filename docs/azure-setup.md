# Guía de documentación — Jira / Azure DevOps

Las historias de usuario de la Tarea 4 **deben** documentarse en un tablero de **Jira** o
**Azure DevOps** (la tarea no acepta PDF, Word, Google Drive ni GitHub README). Las 5 historias
listas para copiar/pegar están en [`docs/user-stories.md`](user-stories.md).

> **Importante (2026):** Azure DevOps retiró los proyectos públicos. Ya no se pueden crear
> proyectos públicos nuevos, por lo que **no existe un enlace anónimo** para el profesor. Para
> cumplir el requisito de "acceso abierto" tenés dos caminos:

---

## Opción A — Azure DevOps + invitar al profesor (si querés Azure)

1. Crear cuenta gratis en <https://dev.azure.com> (cuenta de Microsoft).
2. Crear **organización** y **proyecto** (visibilidad privada, no importa).
3. Ir a **Boards → Work Items → New Work Item → User Story** y crear las 5 historias.
   - Título: `US-01 Inicio de sesión`, `US-02 Gestionar choferes`, etc.
   - Descripción: texto `Como <rol>, quiero <funcionalidad> para <beneficio>`.
   - Criterios de aceptación y rechazo: copiarlos del campo correspondiente de
     `docs/user-stories.md` (en Azure pueden ir en el campo **Acceptance Criteria**).
4. Otorgar acceso al profesor:
   - **Organization settings → Users → Add users**.
   - Agregar `ktejada@itla.edu.do` (y el correo del monitor si lo tenés).
   - Nivel de acceso: **Stakeholder** — es **gratis e ilimitado**.
   - El profesor entra con su cuenta de Microsoft y ve todo el tablero.
5. Compartir el enlace del proyecto (`https://dev.azure.com/{organizacion}/{proyecto}`) en el
   campo "Texto en línea" de la plataforma.

---

## Opción B — Jira free + enlace público (más directo)

1. Crear cuenta gratis en <https://www.atlassian.com> → **Jira Software**.
2. Crear un proyecto con plantilla **Scrum**.
3. En el backlog, crear las 5 historias con el tipo **Story**:
   - **Resumen**: `US-01 Inicio de sesión`, `US-02 Gestionar choferes`, `US-03 Gestionar
     camiones`, `US-04 Gestionar rutas`, `US-05 Registrar horas trabajadas`.
   - **Descripción**: `Como <rol>, quiero <funcionalidad> para <beneficio>`.
   - **Criterios de aceptación**: pegar los criterios de aceptación de `docs/user-stories.md`.
   - **Criterios de rechazo**: pegar los criterios de rechazo de `docs/user-stories.md`.
4. Compartir de forma pública:
   - Abrir cada historia → botón **Share** → **Anyone with the link** (acceso sin login).
   - Alternativa: **Project settings → People → Share with the public**.
5. Compartir el enlace del proyecto en el campo "Texto en línea".

---

## Configuración del tablero (Jira)

- **Proyecto:** plantilla **Scrum**.
- **Columnas:** `To Do → In Progress → Review → Done`.
- **Tipos de ítem:** Story (una por historia de usuario).
- **Dashboard sugerido** (Jira → Dashboards → Create): "Entrega Tarea 4 — Pruebas
  Automatizadas" con los gadgets:
  - **Active Sprints**
  - **Burndown Chart**
  - **Issues in progress**
  - **Two-dimensional filter statistics** (por estado/prioridad)

## Checklist de acceso antes de entregar

- [ ] Repositorio GitHub **público** (o acceso otorgado) — sin esto, **−80%**.
- [ ] Tablero Jira/Azure con las 5 historias y criterios de aceptación y rechazo —
      sin acceso, **−20%**.
- [ ] Enlaces públicos o con acceso abierto (profesor y monitor pueden entrar).
- [ ] Video demostrativo público en **YouTube o OneDrive** (no Google Drive).
- [ ] Reporte HTML y capturas generados en el repositorio.
