# Historias de usuario — Gestión de Transporte

Documentación fuente para el tablero de Jira o Azure DevOps (requisito de la Tarea 4).
Las 5 historias incluyen criterios de **aceptación** (cuándo el caso pasa) y de **rechazo**
(cuándo falla). Mapean 1:1 con los archivos de pruebas Selenium del repositorio.

---

## US-01 — Inicio de sesión

> **Como** administrador, **quiero** iniciar sesión con mis credenciales **para** acceder al
> sistema y administrar los datos de transporte.

**Criterios de aceptación**
- Con credenciales válidas (`admin` / `admin123`) el sistema redirige al panel de control y
  mantiene la sesión activa.
- El menú lateral muestra el nombre, el rol y la opción "Cerrar sesión".
- Al cerrar sesión, el sistema redirige a la pantalla de inicio de sesión.

**Criterios de rechazo**
- Con una contraseña incorrecta se muestra el mensaje *"Usuario o contraseña incorrectos"* y
  el usuario permanece en `/login` sin autenticar.
- Si se envía el formulario con los campos vacíos, el navegador bloquea el envío y no se
  autentica.

**Casos de prueba:** `tests/test_login.py`

---

## US-02 — Gestionar choferes

> **Como** administrador, **quiero** registrar, consultar, editar y eliminar choferes **para**
> mantener actualizado el registro del personal.

**Criterios de aceptación**
- Al crear un chofer con nombre y cédula válidos, el registro aparece en el listado y se
  muestra el mensaje "Chofer creado exitosamente".
- Se puede buscar un chofer por nombre o cédula desde el listado.
- Al editar un chofer, los cambios se guardan y se reflejan en el listado.

**Criterios de rechazo**
- Con el nombre vacío se muestra *"El nombre es obligatorio"* y no se guarda (HTTP 422).
- Con un nombre de más de 200 caracteres se muestra *"El nombre no puede superar los 200
  caracteres"* y no se guarda.
- Con una cédula duplicada se muestra *"Ya existe un chofer con esa cédula"* y no se guarda.
- Un usuario con rol consultor no puede acceder al formulario de creación (se redirige al
  panel de control) ni ve el botón "Nuevo".

**Casos de prueba:** `tests/test_choferes.py`

---

## US-03 — Gestionar camiones

> **Como** administrador, **quiero** registrar, consultar, editar y eliminar camiones **para**
> controlar el parque vehicular.

**Criterios de aceptación**
- Al crear un camión con placa válida, el registro aparece en el listado con su marca, modelo,
  año y capacidad.
- Se puede buscar un camión por placa o marca desde el listado.
- Al editar un camión, los cambios se guardan y se reflejan en el listado.

**Criterios de rechazo**
- Con la placa vacía se muestra *"La placa es obligatoria"* y no se guarda (HTTP 422).
- Con una placa duplicada se muestra *"Ya existe un camión con esa placa"* y no se guarda.

**Casos de prueba:** `tests/test_camiones.py`

---

## US-04 — Gestionar rutas

> **Como** administrador, **quiero** registrar y consultar rutas de transporte (origen, destino,
> distancia) **para** planificar los recorridos.

**Criterios de aceptación**
- Al crear una ruta con origen, destino y distancia mayor que 0, el registro aparece en el
  listado con sus datos.
- Se puede buscar una ruta por origen o destino desde el listado.

**Criterios de rechazo**
- Con el origen vacío se muestra *"El origen es obligatorio"* y no se guarda (HTTP 422).
- Con distancia 0 o negativa se muestra *"La distancia debe ser mayor que 0 y no superar 5000
  km"* y no se guarda.

**Casos de prueba:** `tests/test_rutas.py`

---

## US-05 — Registrar horas trabajadas

> **Como** administrador, **quiero** registrar las horas trabajadas por cada chofer en una ruta y
> fecha determinadas **para** llevar el control de la jornada.

**Criterios de aceptación**
- Al registrar 8 horas de un chofer en una ruta y fecha válidas, el registro aparece en la
  tabla de horas y se muestra el mensaje "Horas registradas exitosamente".
- El valor máximo válido (24 horas) se registra correctamente.

**Criterios de rechazo**
- Con un chofer inexistente se muestra *"El chofer seleccionado no existe"* y no se guarda.
- Con 0 horas o más de 24 horas se muestra *"Las horas deben estar entre 1 y 24"* y no se
  guarda (HTTP 422).

**Casos de prueba:** `tests/test_horas.py`

---

## Referencia — tipos de prueba por flujo

| Historia | Camino feliz | Prueba negativa | Prueba de límites |
| --- | --- | --- | --- |
| US-01 Login | Credenciales válidas → panel | Contraseña incorrecta → error | Campos vacíos bloqueados |
| US-02 Choferes | Crear chofer válido | Nombre vacío → error 422 | Nombre > 200 caracteres; cédula duplicada |
| US-03 Camiones | Crear camión válido | Placa vacía → error 422 | Placa duplicada |
| US-04 Rutas | Crear ruta válida | Origen vacío → error 422 | Distancia 0/negativa |
| US-05 Horas | Registrar 8 horas | Chofer inexistente → error | 0 y 25 horas → error; 24 horas → válido |
