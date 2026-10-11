# Guía de desarrollo – CRUD Médicos y Citas (Svelte + FastAPI)

Oct 11, 2026 · @Daniel Martínez

## Decisiones acordadas

Esta tabla es la fuente de verdad del equipo: los dos usan estos valores tal cual, y quien quiera cambiar uno se lo avisa al otro antes. Con ellas, el frontend y el backend se pueden construir por separado y encajan al integrarlos.

| Tema | Decisión |
| --- | --- |
| Entidades | `Medico` y `Cita`; un médico tiene muchas citas |
| Frontend (C) | SvelteKit con Svelte 5, en JavaScript, funcionando como SPA (sin renderizado en servidor) |
| Backend (D) | FastAPI con SQLAlchemy 2, Pydantic 2 y el controlador `psycopg` 3 |
| Base de datos | PostgreSQL 17 en Docker Compose, con un volumen con nombre para que los datos persistan |
| Versiones mínimas | Python 3.10 o superior (lo exige FastAPI 0.143); Node.js 20.19 o superior, o 22.12 o superior (lo exige Vite) |
| Puertos | Frontend 5173, API 8000, PostgreSQL 5432 |
| Nombres | Tablas, campos y rutas en español, sin tildes y en `snake_case`: `medicos`, `citas`, `fecha_hora` |
| Rutas de la API | Sin barra final: `/medicos`, no `/medicos/` (evita redirecciones y errores de CORS) |
| Identificadores | Números enteros autoincrementales |
| Fechas | Texto ISO 8601 sin zona horaria, por ejemplo `2026-10-12T15:30:00` |
| Errores | JSON con `{"detail": "..."}`: 404 si no existe, 409 si hay conflicto, 422 si el dato es inválido |
| Repositorio | Un solo repositorio con `backend/` y `frontend/` |

La guía de sustentación usaba `/recursos/` con barra final solo como ejemplo. Para el proyecto real valen las rutas de esta guía.

## Almacenamiento: PostgreSQL 17 en Docker con volumen

Su idea es la mejor opción: **PostgreSQL en Docker con un volumen con nombre**. Los datos quedan en el volumen, no dentro del contenedor, así que sobreviven a apagar, reiniciar o recrear el contenedor. Además es una base real, igual en las dos máquinas, y se explica bien en la sustentación.

| Opción | Cómo persisten los datos | Instalación | Cuándo elegirla |
| --- | --- | --- | --- |
| PostgreSQL 17 en Docker (recomendada) | Volumen `pgdata`, fuera del contenedor | Docker Desktop y un `docker compose up` | Es la opción por defecto del equipo |
| SQLite (plan B) | Un archivo `.db` en el disco | Ninguna | Si Docker no funciona en una máquina; se cambia con una sola variable de entorno |
| PostgreSQL en la nube | En el servicio externo | Cuenta y configuración | No la recomiendo: la demo dependería de internet |

Por qué la versión 17 y no la última: la página oficial de la imagen indica que desde PostgreSQL 18 cambió la ruta del volumen. Con la 17 la ruta es la clásica, `/var/lib/postgresql/data`, y evitan ese cambio. Ambos usan exactamente `postgres:17`.

**Reglas para que no se pierdan los datos:**

- `docker compose down` apaga los contenedores y **conserva** los datos.
- `docker compose down -v` **borra el volumen** y con él todos los datos. No lo usen salvo que quieran empezar de cero.
- Cada uno tiene su propia base de datos en su computador. Lo que comparten es el esquema, que lo crea el código, y un script `seed.py` con datos de prueba. Los datos no viajan por Git.
- Para la demo usen **un solo computador**, con la base ya cargada, y antes de exponer hagan un respaldo con `pg_dump` (el comando está en la sección de Docker Compose).

**Plan B con SQLite:** si Docker falla en una máquina, el backend debe poder arrancar solo con cambiar `DATABASE_URL` a `sqlite:///./clinica.db`. Por eso el código del backend no debe usar nada exclusivo de PostgreSQL.

## Estructura del repositorio y flujo de Git

Un solo repositorio con una carpeta por lado. Como cada uno trabaja casi siempre en su carpeta, los conflictos de Git son raros. Para dos entidades alcanza con un archivo por capa (`models.py`, `schemas.py`); en la diapositiva de estructura muestren el árbol real al final.

```text
clinica/                      # raíz del repositorio (elijan el nombre)
├── docker-compose.yml        # PostgreSQL con volumen
├── .env.example              # variables de PostgreSQL (el .env real no va a Git)
├── .gitignore
├── README.md
├── backend/                  # FastAPI (D): Modelo + Controlador
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # crea la app, CORS y registra los routers
│   │   ├── database.py       # motor y sesión de SQLAlchemy
│   │   ├── models.py         # Modelo: tablas Medico y Cita
│   │   ├── schemas.py        # Modelo: esquemas Pydantic
│   │   └── routers/
│   │       ├── medicos.py    # Controlador
│   │       └── citas.py      # Controlador
│   ├── seed.py               # datos de prueba
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 # SvelteKit (C): Vista
    ├── src/
    │   ├── lib/
    │   │   ├── api.js        # todas las llamadas fetch a FastAPI
    │   │   └── components/   # formularios y tablas reutilizables
    │   └── routes/
    │       ├── +layout.js    # desactiva el renderizado en servidor
    │       ├── +layout.svelte
    │       ├── +page.svelte  # inicio
    │       ├── medicos/+page.svelte
    │       └── citas/+page.svelte
    ├── .env.example
    └── package.json
```

**Archivo `.gitignore` en la raíz:**

```text
# Python
backend/.venv/
__pycache__/
*.pyc
# Node y SvelteKit
frontend/node_modules/
frontend/.svelte-kit/
frontend/build/
# Secretos y datos locales
.env
*.db
```

**Reglas de trabajo con Git:**

1. Uno de los dos crea el repositorio en GitHub y agrega al otro como colaborador. Hacen el primer commit juntos con la estructura y el `docker-compose.yml` (sección siguiente).
2. `main` siempre debe arrancar. Cada uno trabaja en su rama (`feat/backend-medicos`, `feat/frontend-medicos`) y la une a `main` cuando funciona.
3. Antes de empezar a trabajar: `git pull`. Después de cada avance pequeño: `git add`, `git commit` y `git push`.
4. Los archivos compartidos (`docker-compose.yml`, `README.md`, el contrato de la API) solo se cambian avisando al otro.
5. Nunca suban un `.env` real ni una contraseña. Suban solo los `.env.example`.

## Preparar el entorno (los dos)

Instalen y comprueben todo esta tarde, en este orden: Docker Desktop es lo que más tarda y lo que más falla, y es mejor descubrirlo hoy.

| Herramienta | Versión | Comprobar con |
| --- | --- | --- |
| Docker Desktop | Reciente, con Docker Compose v2 | `docker --version` y `docker compose version` |
| Python | 3.10 o superior | `python --version` (en Windows también `py --version`) |
| Node.js | 20.19 o superior, o 22.12 o superior | `node --version` |
| Git | Cualquier versión reciente | `git --version` |
| Editor | VS Code con las extensiones Python y Svelte for VS Code | Abrir la carpeta del repositorio |

Si un comando no responde, esa herramienta no está instalada o no está en el PATH. Cierren y vuelvan a abrir la terminal después de instalar.

**Cosas a tener en cuenta:**

- En Windows, Docker Desktop necesita la virtualización activada y WSL 2. Si no arranca y no se resuelve en 20 minutos, pasen al plan B (SQLite) en esa máquina y no pierdan más tiempo.
- Docker Desktop debe estar abierto y en estado "running" antes de usar `docker compose`.
- Para mirar el contenido de la base de datos no necesitan instalar nada más: sirve `docker compose exec db psql` (en la sección de Docker Compose). Si quieren una interfaz gráfica, DBeaver es opcional.

**Primeros pasos, después del primer commit del repositorio:**

```bash
git clone <url-del-repositorio>
cd clinica
cp .env.example .env              # en PowerShell: Copy-Item .env.example .env
```

El `.env` de la raíz es el que lee Docker Compose. Cada lado tendrá además su propio `.env` (se indica en la sección de configuración inicial).

## Base de datos con Docker Compose

Uno de los dos crea estos dos archivos en la raíz del repositorio, los sube a Git y el otro hace `git pull`. Desde ese momento los dos tienen la misma base de datos.

**`docker-compose.yml`**

```yaml
services:
  db:
    image: postgres:17
    container_name: clinica_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  pgdata:
```

**`.env.example`** (cada uno lo copia a `.env`; este `.env` no va a Git)

```text
POSTGRES_USER=clinica
POSTGRES_PASSWORD=clinica123
POSTGRES_DB=clinica
```

Si ya tienen PostgreSQL instalado en el computador y el puerto 5432 está ocupado, cambien la línea de puertos a `"5433:5432"` y usen el puerto 5433 en `DATABASE_URL`. Lo cambia cada uno en su máquina, sin subirlo a Git.

**Comandos del día a día** (desde la raíz del repositorio, con Docker Desktop abierto):

```bash
docker compose up -d          # levanta la base de datos en segundo plano
docker compose ps             # db debe aparecer como running (healthy)
docker compose logs -f db     # ver los registros; Ctrl+C para salir
docker compose exec db psql -U clinica -d clinica   # consola SQL; \dt lista tablas, \q sale
docker compose stop           # apaga y conserva todo
docker compose down           # quita el contenedor y conserva los datos
docker compose down -v        # BORRA el volumen y todos los datos: cuidado
```

**Prueba de persistencia (háganla una vez, es la garantía de que no pierden datos):**

```bash
docker compose up -d
docker compose exec db psql -U clinica -d clinica -c "CREATE TABLE prueba (id int); INSERT INTO prueba VALUES (1);"
docker compose down
docker compose up -d
docker compose exec db psql -U clinica -d clinica -c "SELECT * FROM prueba;"   # debe devolver la fila 1
docker compose exec db psql -U clinica -d clinica -c "DROP TABLE prueba;"
```

**Respaldo antes de la demo** (y para restaurar en otra máquina). Estos comandos evitan las redirecciones `>` y `<`, que se comportan distinto en PowerShell:

```bash
docker compose exec db pg_dump -U clinica -d clinica -f /tmp/respaldo.sql
docker compose cp db:/tmp/respaldo.sql ./respaldo.sql

# restaurar
docker compose cp ./respaldo.sql db:/tmp/respaldo.sql
docker compose exec db psql -U clinica -d clinica -f /tmp/respaldo.sql
```

Agreguen `respaldo.sql` al `.gitignore`.

Un detalle que sorprende: las variables `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB` solo se leen cuando el volumen está vacío, la primera vez. Si cambian la contraseña después, no pasa nada hasta que borren el volumen con `down -v`. Por eso conviene que los dos usen los mismos valores desde el inicio.

## Modelo de datos: Médico y Cita

Hay dos entidades y una relación de uno a muchos: un médico tiene muchas citas y cada cita pertenece a un solo médico. No hay entidad Paciente: el paciente es solo un nombre dentro de la cita, para que el CRUD siga siendo sencillo.

&#91;embedded content: relación 1 a N · Medico y Cita\]

La clave foránea `medico_id` de Cita apunta al `id` de Medico; de ahí salen las reglas de 404 y 409.

**Tabla `medicos`**

| Campo | Tipo | Reglas |
| --- | --- | --- |
| `id` | entero | Clave primaria, autoincremental |
| `nombre` | texto | Obligatorio, de 2 a 100 caracteres |
| `especialidad` | texto | Obligatorio, de 2 a 100 caracteres |
| `correo` | texto | Obligatorio, único |

**Tabla `citas`**

| Campo | Tipo | Reglas |
| --- | --- | --- |
| `id` | entero | Clave primaria, autoincremental |
| `medico_id` | entero | Obligatorio, clave foránea hacia `medicos.id` |
| `paciente` | texto | Obligatorio, de 2 a 100 caracteres |
| `fecha_hora` | fecha y hora | Obligatorio, sin zona horaria y no puede estar en el pasado |
| `motivo` | texto | Opcional, hasta 200 caracteres |

**Reglas de negocio:**

- Si una cita usa un `medico_id` que no existe, la API responde 404.
- Un médico que tiene citas no se puede eliminar: la API responde 409 con un mensaje claro.
- Un médico no puede tener dos citas en la misma `fecha_hora`; la API responde 409.
- No se puede agendar ni actualizar una cita a una fecha y hora que ya hayan pasado; la API responde 422.

**Datos de prueba** que carga `seed.py`. Los dos usan estos mismos datos en los ensayos de la demo, y el script debe poder correrse varias veces sin duplicar nada.

| Médico | Especialidad | Correo |
| --- | --- | --- |
| Laura Gómez | Medicina general | laura.gomez@clinica.test |
| Andrés Ruiz | Pediatría | andres.ruiz@clinica.test |
| Sofía Mejía | Dermatología | sofia.mejia@clinica.test |

| Paciente | Médico | Fecha y hora | Motivo |
| --- | --- | --- | --- |
| Camila Torres | Laura Gómez | 2026-10-12T09:00:00 | Control general |
| Mateo Rojas | Andrés Ruiz | 2026-10-12T10:30:00 | Vacunación |
| Valeria Ortiz | Sofía Mejía | 2026-10-13T08:00:00 | Revisión de piel |
| Daniel Peña | Laura Gómez | 2026-10-13T11:00:00 | Dolor de cabeza |

## Contrato de la API

Este contrato es lo que permite que el frontend y el backend se construyan en paralelo: C programa contra estas rutas y estos JSON, D los implementa tal cual, y al integrar todo encaja. La API vive en `http://localhost:8000`, habla JSON y no usa barra final en las rutas.

| Método | Ruta | Cuerpo | Éxito | Errores |
| --- | --- | --- | --- | --- |
| GET | `/salud` | no | 200 `{"estado": "ok"}` | no |
| GET | `/medicos` | no | 200, lista de médicos | no |
| POST | `/medicos` | `MedicoIn` | 201, `MedicoOut` | 422, 409 si el correo ya existe |
| GET | `/medicos/{id}` | no | 200, `MedicoOut` | 404 |
| PUT | `/medicos/{id}` | `MedicoIn` | 200, `MedicoOut` | 404, 422, 409 si el correo ya existe |
| DELETE | `/medicos/{id}` | no | 204 sin cuerpo | 404, 409 si tiene citas |
| GET | `/citas` | no | 200, lista de citas | no |
| POST | `/citas` | `CitaIn` | 201, `CitaOut` | 404 si el médico no existe, 409 si el médico ya tiene una cita en esa fecha y hora, 422 si la fecha y hora ya pasó |
| GET | `/citas/{id}` | no | 200, `CitaOut` | 404 |
| PUT | `/citas/{id}` | `CitaIn` | 200, `CitaOut` | 404, 409 si el médico ya tiene otra cita en esa fecha y hora, 422 si la fecha y hora ya pasó |
| DELETE | `/citas/{id}` | no | 204 sin cuerpo | 404 |

Los errores de conflicto por horario duplicado usan `{"detail": "Ya existe una cita para este médico en esa fecha y hora"}`.

**Formas de los datos.** `PUT` reemplaza el recurso completo: el frontend siempre envía todos los campos.

```json
// MedicoIn (cuerpo de POST y PUT /medicos)
{
  "nombre": "Laura Gómez",
  "especialidad": "Medicina general",
  "correo": "laura.gomez@clinica.test"
}

// MedicoOut (respuesta): lo mismo más el id
{ "id": 1, "nombre": "Laura Gómez", "especialidad": "Medicina general", "correo": "laura.gomez@clinica.test" }

// CitaIn (cuerpo de POST y PUT /citas)
{
  "medico_id": 1,
  "paciente": "Camila Torres",
  "fecha_hora": "2026-10-12T09:00:00",
  "motivo": "Control general"
}

// CitaOut (respuesta): incluye el médico anidado
{
  "id": 1,
  "medico_id": 1,
  "paciente": "Camila Torres",
  "fecha_hora": "2026-10-12T09:00:00",
  "motivo": "Control general",
  "medico": { "id": 1, "nombre": "Laura Gómez", "especialidad": "Medicina general" }
}
```

La respuesta de una cita trae el médico anidado para que la tabla muestre su nombre sin una segunda llamada, y trae también `medico_id` para precargar el formulario de edición. Los comentarios `//` de los ejemplos son solo explicativos: el JSON real no los lleva.

**Formato de los errores.** Los mensajes están en español y son exactos para que el frontend pueda mostrarlos tal cual:

```json
// 404
{ "detail": "Médico no encontrado" }
{ "detail": "Cita no encontrada" }

// 409
{ "detail": "No se puede eliminar un médico con citas" }
{ "detail": "Ya existe un médico con ese correo" }
{ "detail": "Ya existe una cita para este médico en esa fecha y hora" }

// 422 (lo genera FastAPI solo): aquí detail es una LISTA
{ "detail": [ { "loc": ["body", "nombre"], "msg": "String should have at least 2 characters", "type": "string_too_short" } ] }
```

La misma validación 422 aplica si `fecha_hora` está en el pasado; el mensaje será `No se puede agendar una cita en el pasado`.

Cuidado en el frontend: `detail` es un texto en los errores 404 y 409, pero una lista en el 422. La función que lee los errores debe manejar los dos casos.

**Convenciones que cumplen los dos:**

- Todo el frontend llama a la API desde un único archivo, `src/lib/api.js`, y nunca desde los componentes. Así, si cambia una ruta, se corrige en un solo lugar.
- El backend permite CORS para `http://localhost:5173` y `http://127.0.0.1:5173`, con todos los métodos y cabeceras.
- Si hace falta cambiar el contrato (un campo, una ruta, un código), se cambia primero aquí, en esta guía, y se avisa al otro. Nadie lo cambia solo en su código.
- Las rutas `GET` de listas no paginan: con tan pocos datos no hace falta.

## Configuración inicial de cada lado

Esta sección deja los dos lados arrancando y hablándose, sin implementar todavía el CRUD. La meta es una **prueba de humo**: Svelte llama a `/salud` en FastAPI y muestra "ok". Si eso funciona, CORS, puertos y variables de entorno están bien, y lo que falte es solo código del CRUD.

### Backend con FastAPI (D)

```bash
cd backend
python -m venv .venv
# activar el entorno virtual (uno de los tres):
#   PowerShell:    .venv\Scripts\Activate.ps1
#   CMD:           .venv\Scripts\activate.bat
#   macOS/Linux:   source .venv/bin/activate
pip install -r requirements.txt
```

**`backend/requirements.txt`** (sin versiones fijas; cuando todo funcione, pueden fijarlas con `pip freeze`):

```text
fastapi[standard]
sqlalchemy>=2.0
psycopg[binary]>=3.2
python-dotenv
```

**`backend/.env.example`** (cada uno lo copia a `backend/.env`):

```text
DATABASE_URL=postgresql+psycopg://clinica:clinica123@localhost:5432/clinica
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Para el plan B con SQLite, `DATABASE_URL` pasa a ser `sqlite:///./clinica.db`.

**`backend/app/main.py`** mínimo, con CORS y la ruta `/salud` (dejen vacío el `__init__.py`):

```python
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
origenes = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(title="Clínica API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/salud")
def salud():
    return {"estado": "ok"}
```

**Arrancar y comprobar** (desde `backend/`, con el entorno virtual activo):

```bash
uvicorn app.main:app --reload --port 8000
```

Abran `http://localhost:8000/docs`: debe verse Swagger con la ruta `/salud`. El comando de arranque de la guía de sustentación era `uvicorn main:app`; con esta estructura de carpetas el correcto es `uvicorn app.main:app`.

### Frontend con SvelteKit (C)

```bash
npx sv create frontend --template minimal --types jsdoc
cd frontend
npm install
```

El asistente de `sv create` hace algunas preguntas más. Respondan que no a los complementos adicionales y elijan npm como gestor de paquetes. La opción `--types jsdoc` deja el proyecto en JavaScript con comentarios de tipos, sin la complejidad de TypeScript.

**`frontend/.env.example`** (cada uno lo copia a `frontend/.env`):

```text
VITE_API_URL=http://localhost:8000
```

**`frontend/src/routes/+layout.js`**: convierte SvelteKit en una SPA que hace todo en el navegador, sin renderizado en servidor. Así el modelo mental es el de la sustentación: Svelte en el navegador llama con `fetch` a la API.

```js
export const ssr = false;
```

**`frontend/src/routes/+page.svelte`** para la prueba de humo:

```svelte
<script>
  import { onMount } from 'svelte';

  const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
  let estado = $state('comprobando...');

  onMount(async () => {
    try {
      const res = await fetch(`${API}/salud`);
      estado = (await res.json()).estado;
    } catch {
      estado = 'sin conexión con la API';
    }
  });
</script>

<h1>Clínica</h1>
<p>Estado de la API: {estado}</p>
```

**Arrancar y comprobar:**

```bash
npm run dev
```

Abran `http://localhost:5173`. Con el backend encendido debe decir "Estado de la API: ok". Si dice "sin conexión", revisen la consola del navegador: casi siempre es CORS o un puerto equivocado.

**El hito 0 está cumplido cuando:** la base de datos aparece como `healthy` en `docker compose ps`, `/docs` abre en el backend y la página de Svelte muestra "ok". Los dos lo comprueban en su propio computador y lo confirman entre ustedes.

## Cómo integrar sin sorpresas

Tienen hasta el lunes 12 de octubre a las 4:40 p.m. La forma de no llegar con el CRUD roto es integrar **temprano y en pedazos pequeños**: cada hito termina con los dos lados funcionando juntos, no con un lado terminado y el otro por empezar. Las ventanas son una sugerencia; ajústenlas a su horario.

| Hito | Quién | Está listo cuando | Ventana sugerida |
| --- | --- | --- | --- |
| 0. Entorno y prueba de humo | Los dos | `docker compose ps` en `healthy`, `/docs` abre y Svelte muestra "ok" | Hoy, hasta las 6:00 p.m. |
| 1. Médicos de punta a punta | D: modelos, esquemas, rutas de `/medicos` y `seed.py`. C: página `/medicos` con lista, crear, editar y eliminar | Se crea, edita y elimina un médico desde la pantalla y sigue ahí al recargar | Hoy, de 6:00 a 10:00 p.m. |
| 2. Citas de punta a punta | D: rutas de `/citas` con el médico anidado. C: página `/citas` con un desplegable de médicos | Se crea, edita y elimina una cita; la tabla muestra el nombre del médico | Lunes, de 7:00 a 11:00 a.m. |
| 3. Errores y pulido | Los dos | Se ven en pantalla los mensajes de 404, 409 y 422, y no se rompe nada con el backend apagado | Lunes, de 11:00 a.m. a 1:00 p.m. |
| 4. Congelar y ensayar | Los dos | No se agrega nada nuevo; hay respaldo de la base de datos, capturas de la demo y un ensayo cronometrado | Lunes, de 1:00 a 3:30 p.m. |

Después de la 1:00 p.m. del lunes no se agregan funciones nuevas, solo arreglos. Un CRUD sencillo que funciona vale más que uno completo que falla en vivo.

**Orden recomendado para que nadie espere al otro:**

- D publica primero `GET /medicos` y `POST /medicos`, aunque lo demás no esté. Con eso C ya puede probar la lista y el formulario con datos reales.
- Mientras tanto C construye la pantalla contra el contrato y usa `/docs` de Swagger para ver qué devuelve cada ruta.
- Cada vez que uno sube algo a `main`, avisa por el chat del grupo con una frase: "ya están GET y POST de médicos".
- Si C necesita un dato que el contrato no tiene, lo pide y se agrega al contrato antes de programarlo.

**Pruebas de integración.** Antes del ensayo, los dos las pasan juntas, en pantalla y no solo con Swagger:

- [ ] Crear un médico válido: aparece en la lista.
- [ ] Crear un médico con el correo repetido: se ve el mensaje del 409.
- [ ] Crear un médico con el nombre vacío: se ve el mensaje de validación del 422.
- [ ] Editar un médico y recargar la página: el cambio sigue ahí.
- [ ] Eliminar un médico sin citas: desaparece de la lista.
- [ ] Eliminar un médico con citas: se ve el mensaje del 409 y el médico sigue en la lista.
- [ ] Crear una cita eligiendo el médico en el desplegable: aparece con el nombre del médico.
- [ ] Editar y eliminar una cita.
- [ ] Apagar con `docker compose down` y volver a encender con `up -d`: los datos siguen.
- [ ] Apagar el backend: el frontend muestra un mensaje de error y no se queda en blanco.

## Problemas típicos y su solución

Estos son los fallos que más tiempo hacen perder en una configuración como esta. Busquen aquí el síntoma antes de pedir ayuda.

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| `docker compose` no se conecta con el daemon de Docker | Docker Desktop está cerrado o aún arrancando | Abrirlo y esperar a que diga "running" |
| El puerto 5432 "is already allocated" | Hay otro PostgreSQL usando ese puerto | Cambiar a `"5433:5432"` en el compose y usar 5433 en `DATABASE_URL` |
| `password authentication failed for user` | `DATABASE_URL` no coincide con el `.env` de la raíz, o cambiaron la contraseña con el volumen ya creado | Igualar los valores; si hace falta empezar de cero, `docker compose down -v` (borra los datos) |
| `connection refused` al arrancar el backend | La base de datos no está encendida o aún no está `healthy` | `docker compose up -d` y esperar a `healthy` en `docker compose ps` |
| El navegador dice "blocked by CORS policy" | El origen del frontend no está en `CORS_ORIGINS`; por ejemplo, abrieron `127.0.0.1` y solo está `localhost` | Dejar los dos orígenes en `backend/.env` y reiniciar el backend |
| `import.meta.env.VITE_API_URL` es `undefined` | El `frontend/.env` se creó o cambió con el servidor encendido | Detener `npm run dev` y volver a ejecutarlo |
| `ModuleNotFoundError: No module named 'app'` | `uvicorn` se ejecutó desde otra carpeta, o falta `app/__init__.py` | Ejecutarlo desde `backend/` y crear el archivo vacío |
| PowerShell no deja ejecutar `Activate.ps1` | La política de scripts está restringida | Usar CMD (`activate.bat`) o ejecutar `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` en esa terminal |
| `pip install` instala en el Python global | El entorno virtual no está activo; falta `(.venv)` en el prompt | Activarlo y repetir la instalación |
| Un `POST` falla o se redirige con otra ruta | El frontend llama a `/medicos/` con barra final y el backend la define sin ella | Usar siempre rutas sin barra final, como dice el contrato |
| La lista no se actualiza después de crear o eliminar | El frontend no vuelve a pedir la lista tras la operación | Después de cada `POST`, `PUT` o `DELETE` correcto, volver a llamar a `GET` y reasignar el estado |

## Fuentes consultadas

Páginas abiertas el 11 de octubre de 2026:

- Versiones de PostgreSQL, ruta del volumen en la versión 17 y en la 18, y variables de entorno: [imagen oficial de PostgreSQL en Docker Hub](https://hub.docker.com/_/postgres).
- Versión de Node.js que exige Vite (20.19 o superior, o 22.12 o superior): [guía de Vite](https://vite.dev/guide/).
- Comando `sv create` y sus opciones de plantilla y tipos: [documentación de la CLI de Svelte](https://svelte.dev/docs/cli/sv-create).
- Python 3.10 o superior para FastAPI 0.143.0: [FastAPI en PyPI](https://pypi.org/project/fastapi/).

Lo demás (contrato de la API, modelo de datos, hitos, comandos de Docker Compose, configuración de CORS y la solución de problemas) es diseño y explicación técnica de esta guía. Pruébenlo en su computador y ajusten lo que haga falta, sobre todo los comandos de activación del entorno virtual según su sistema operativo.
